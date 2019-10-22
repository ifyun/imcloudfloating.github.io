---
title: Spring Boot & MyBatis 实现乐观锁和悲观锁
date: 2019-09-04 20:25:00 +0800
categories: [Spring Boot, 锁]
tags: [Spring Boot]
seo:
  date_modified: 2019-10-22 15:24:11 +0800
---

以转账操作为例，实现并测试乐观锁和悲观锁。

全部代码：[https://github.com/imcloudfloating/Lock_Demo](https://github.com/imcloudfloating/Lock_Demo)

## 死锁问题

当 A, B 两个账户同时向对方转账时，会出现如下情况：

| 时刻 | 事务 1 (A 向 B 转账)                  | 事务 2 (B 向 A 转账)                  |
| ---- | ------------------------------------- | ------------------------------------- |
| T1   | Lock A                                | Lock B                                |
| T2   | Lock B (由于事务 2 已经 Lock A，等待) | Lock A (由于事务 1 已经 Lock B，等待) |

由于两个事务都在等待对方释放锁，于是死锁产生了，解决方案：按照主键的大小来加锁，总是先锁主键较小或较大的那行数据。

## 建立数据表并插入数据（MySQL）

```sql
create table account
(
    id      int auto_increment
        primary key,
    deposit decimal(10, 2) default 0.00 not null,
    version int            default 0    not null
);

INSERT INTO vault.account (id, deposit, version) VALUES (1, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (2, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (3, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (4, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (5, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (6, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (7, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (8, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (9, 1000, 0);
INSERT INTO vault.account (id, deposit, version) VALUES (10, 1000, 0);
```

## Mapper 文件

悲观锁使用 select ... for update，乐观锁使用 version 字段。

```xml
<?xml version="1.0" encoding="UTF-8" ?>
<!DOCTYPE mapper PUBLIC "-//mybatis.org//DTD Mapper 3.0//EN"
        "http://mybatis.org/dtd/mybatis-3-mapper.dtd" >
<mapper namespace="com.cloud.demo.mapper.AccountMapper">
    <select id="selectById" resultType="com.cloud.demo.model.Account">
        select *
        from account
        where id = #{id}
    </select>
    <update id="updateDeposit" keyProperty="id" parameterType="com.cloud.demo.model.Account">
        update account
        set deposit=#{deposit},
            version = version + 1
        where id = #{id}
          and version = #{version}
    </update>
    <select id="selectByIdForUpdate" resultType="com.cloud.demo.model.Account">
        select *
        from account
        where id = #{id} for
        update
    </select>
    <update id="updateDepositPessimistic" keyProperty="id" parameterType="com.cloud.demo.model.Account">
        update account
        set deposit=#{deposit}
        where id = #{id}
    </update>
    <select id="getTotalDeposit" resultType="java.math.BigDecimal">
        select sum(deposit) from account;
    </select>
</mapper>
```

## Mapper 接口

```java
@Component
public interface AccountMapper {
    Account selectById(int id);
    Account selectByIdForUpdate(int id);
    int updateDepositWithVersion(Account account);
    void updateDeposit(Account account);
    BigDecimal getTotalDeposit();
}
```

## Account POJO

```java
@Data
public class Account {
    private int id;
    private BigDecimal deposit;
    private int version;
}
```

## AccountService

在 transferOptimistic 方法上有个自定义注解 @Retry，这个用来实现乐观锁失败后重试。

```java
@Slf4j
@Service
public class AccountService {

    public enum Result{
        SUCCESS,
        DEPOSIT_NOT_ENOUGH,
        FAILED,
    }

    @Resource
    private AccountMapper accountMapper;

    private BiPredicate<BigDecimal, BigDecimal> isDepositEnough = (deposit, value) -> deposit.compareTo(value) > 0;

    /**
     * 转账操作，悲观锁
     *
     * @param fromId 扣款账户
     * @param toId   收款账户
     * @param value  金额
     */
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public Result transferPessimistic(int fromId, int toId, BigDecimal value) {
        Account from, to;

        try {
            // 先锁 id 较大的那行，避免死锁
            if (fromId > toId) {
                from = accountMapper.selectByIdForUpdate(fromId);
                to = accountMapper.selectByIdForUpdate(toId);
            } else {
                to = accountMapper.selectByIdForUpdate(toId);
                from = accountMapper.selectByIdForUpdate(fromId);
            }
        } catch (Exception e) {
            log.error(e.getMessage());
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            return Result.FAILED;
        }

        if (!isDepositEnough.test(from.getDeposit(), value)) {
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            log.info(String.format("Account %d is not enough.", fromId));
            return Result.DEPOSIT_NOT_ENOUGH;
        }

        from.setDeposit(from.getDeposit().subtract(value));
        to.setDeposit(to.getDeposit().add(value));

        accountMapper.updateDeposit(from);
        accountMapper.updateDeposit(to);

        return Result.SUCCESS;
    }

    /**
     * 转账操作，乐观锁
     *  @param fromId 扣款账户
     * @param toId   收款账户
     * @param value  金额
     */
    @Retry
    @Transactional(isolation = Isolation.REPEATABLE_READ)
    public Result transferOptimistic(int fromId, int toId, BigDecimal value) {
        Account from = accountMapper.selectById(fromId),
                to = accountMapper.selectById(toId);

        if (!isDepositEnough.test(from.getDeposit(), value)) {
            TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
            return Result.DEPOSIT_NOT_ENOUGH;
        }

        from.setDeposit(from.getDeposit().subtract(value));
        to.setDeposit(to.getDeposit().add(value));

        int r1, r2;

        // 先锁 id 较大的那行，避免死锁
        if (from.getId() > to.getId()) {
            r1 = accountMapper.updateDepositWithVersion(from);
            r2 = accountMapper.updateDepositWithVersion(to);
        } else {
            r2 = accountMapper.updateDepositWithVersion(to);
            r1 = accountMapper.updateDepositWithVersion(from);
        }

        if (r1 < 1 || r2 < 1) {
            // 失败，抛出重试异常，执行重试
            throw new RetryException("Transfer failed, retry.");
        } else {
            return Result.SUCCESS;
        }
    }
}
```

## 使用Spring AOP 实现乐观锁失败后重试

### 自定义注解 Retry

```java
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.METHOD)
public @interface Retry {
    int value() default 3; // 重试次数
}
```

### 重试异常 RetryException

```java
public class RetryException extends RuntimeException {
    public RetryException(String message) {
        super(message);
    }
}
```

### 重试的切面类

tryAgain 方法使用了 @Around 注解（表示环绕通知），可以决定目标方法在何时执行，或者不执行，以及自定义返回结果。这里首先通过 ProceedingJoinPoint.proceed() 方法执行目标方法，如果抛出了重试异常，那么重新执行直到满三次，三次都不成功则回滚并返回 FAILED。

```java
@Slf4j
@Aspect
@Component
public class RetryAspect {

    @Pointcut("@annotation(com.cloud.demo.annotation.Retry)")
    public void retryPointcut() {

    }

    @Around("retryPointcut() && @annotation(retry)")
    @Transactional(isolation = Isolation.READ_COMMITTED)
    public Object tryAgain(ProceedingJoinPoint joinPoint, Retry retry) throws Throwable {
        int count = 0;
        do {
            count++;
            try {
                return joinPoint.proceed();
            } catch (RetryException e) {
                if (count > retry.value()) {
                    log.error("Retry failed!");
                    TransactionAspectSupport.currentTransactionStatus().setRollbackOnly();
                    return AccountService.Result.FAILED;
                }
            }
        } while (true);
    }
}
```

## 单元测试

用多个线程模拟并发转账，经过测试，悲观锁除了账户余额不足，或者数据库连接不够以及等待超时，全部成功；乐观锁即使加了重试，成功的线程也很少，500 个平均也就十几个成功。

所以对于写多读少的操作，使用悲观锁，对于读多写少的操作，可以使用乐观锁。

> 完整代码请见 Github：[https://github.com/imcloudfloating/Lock_Demo](https://github.com/imcloudfloating/Lock_Demo)。

```java
@Slf4j
@SpringBootTest
@RunWith(SpringRunner.class)
class AccountServiceTest {

    // 并发数
    private static final int COUNT = 500;

    @Resource
    AccountMapper accountMapper;

    @Resource
    AccountService accountService;

    private CountDownLatch latch = new CountDownLatch(COUNT);
    private List<Thread> transferThreads = new ArrayList<>();
    private List<Pair<Integer, Integer>> transferAccounts = new ArrayList<>();

    @BeforeEach
    void setUp() {
        Random random = new Random(currentTimeMillis());
        transferThreads.clear();
        transferAccounts.clear();

        for (int i = 0; i < COUNT; i++) {
            int from = random.nextInt(10) + 1;
            int to;
            do{
                to = random.nextInt(10) + 1;
            } while (from == to);
            transferAccounts.add(new Pair<>(from, to));
        }
    }

    /**
     * 测试悲观锁
     */
    @Test
    void transferByPessimisticLock() throws Throwable {
        for (int i = 0; i < COUNT; i++) {
            transferThreads.add(new Transfer(i, true));
        }
        for (Thread t : transferThreads) {
            t.start();
        }
        latch.await();

        Assertions.assertEquals(accountMapper.getTotalDeposit(),
                BigDecimal.valueOf(10000).setScale(2, RoundingMode.HALF_UP));
    }

    /**
     * 测试乐观锁
     */
    @Test
    void transferByOptimisticLock() throws Throwable {
        for (int i = 0; i < COUNT; i++) {
            transferThreads.add(new Transfer(i, false));
        }
        for (Thread t : transferThreads) {
            t.start();
        }
        latch.await();

        Assertions.assertEquals(accountMapper.getTotalDeposit(),
                BigDecimal.valueOf(10000).setScale(2, RoundingMode.HALF_UP));
    }

    /**
     * 转账线程
     */
    class Transfer extends Thread {
        int index;
        boolean isPessimistic;

        Transfer(int i, boolean b) {
            index = i;
            isPessimistic = b;
        }

        @Override
        public void run() {
            BigDecimal value = BigDecimal.valueOf(
                    new Random(currentTimeMillis()).nextFloat() * 100
            ).setScale(2, RoundingMode.HALF_UP);

            AccountService.Result result = AccountService.Result.FAILED;
            int fromId = transferAccounts.get(index).getKey(),
                    toId = transferAccounts.get(index).getValue();
            try {
                if (isPessimistic) {
                    result = accountService.transferPessimistic(fromId, toId, value);
                } else {
                    result = accountService.transferOptimistic(fromId, toId, value);
                }
            } catch (Exception e) {
                log.error(e.getMessage());
            } finally {
                if (result == AccountService.Result.SUCCESS) {
                    log.info(String.format("Transfer %f from %d to %d success", value, fromId, toId));
                }
                latch.countDown();
            }
        }
    }
}
```

## MySQL 配置

```
innodb_rollback_on_timeout='ON'
max_connections=1000
innodb_lock_wait_timeout=500
```

