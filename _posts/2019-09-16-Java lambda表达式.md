---
title: Java lambda表达式
date: 2019-09-16 23:26 +0800
categories: [Java]
tags: [Java, 函数式编程]
seo:
  date_modified: 2019-10-23 19:53:37 +0800
---

lambda 表达式是一个可传递的代码块，可以在以后执行一次或多次。

## lambda 表达式的语法

参数，箭头（->）以及一个表达式或代码块：

```java
(String first, String second) -> {
    if (first.length() < second.length())
        return -1;
    else if (first.length() > second.length())
        return 1;
    else
        return 0;
}
```

即使没有参数，也要提供空括号：

```java
() -> {
    for (int i = 100; i >= 0; i--)
        System.out.println(i);
}
```

如果可以推导出一个 lambda 表达式的参数类型，则可以忽略其类型：

```java
Comparator<String> cmp = (first, second) -> first.length() - second.length();
```

在这里编译器可以推导出 first 和 second 必然是字符串，因为这个 lambda 表达式将赋给一个字符串比较器。

如果只有一个参数，且类型可以推导得出，可以省略小括号：

```java
ActionListener listener
	= event -> System.out.println("The time is " + new Date());
```

无需指定 lamdba 表达式的返回类型。lambda 表达式的返回类型总是会由上下文推导得出。例如下面的表达式可以在需要 int 类型结果的上下文中使用：

```java
(String first, String second) -> first.length() - second.length();
```

> 如果一个 lambda 表达式只在某些分支返回一个值，在另外一些分支不返回值是不合法的。

## 函数式接口

对于只有一个抽象方法的接口，需要这种接口的对象时，就可以提供一个 lambda 表达式。这种接口称为函数式接口。比如 Arrays.sort 方法，它的第二个参数需要一个 Comparator 实例，Comparator 就是只有一个方法的接口，所以可以传递一个 lambda 表达式：

```java
Arrays.sort(words, (first, second) -> first.length() - second.length());
```

在 Java 中，对 lambda 表达式所能做的也只是能转换为函数式接口。在其他支持函数字面量的语言中，可以声明函数类型，可以使用变量保存函数表达式。

> 不能把 lambda 表达式赋给类型为 Object 的变量，Object 不是一个函数式接口。

Java API 在java.util.function 包中定义了很多非常通用的函数式接口。比如 BiFunction<T, U, R> 描述了参数类型为 T 和 U 而返回类型为 R 的函数。可以把字符串比较的 lambda 表达式保存在这个类型的变量中：

```java
BiFunction<String, String, Integer> cmp
	= (first, second) -> first.length() - second.length();
```

java.util.function 包中有一个很有用的接口 Predicate：

```java
public interface Predicate<T> {
    boolean test(T t);
    ...
}
```

ArrayList 类有一个 removeIf 方法，它的参数就是一个 Predicate：

```java
list.removeIf(e -> e == null);	// 删除所有 null 值
```

## 常用的函数式接口

| 函数式接口          | 参数类型 | 返回类型 | 抽象方法名 | 描述                         | 其他方法                   |
| ------------------- | -------- | -------- | ---------- | ---------------------------- | -------------------------- |
| Runnable            | 无       | void     | run        | 作为无参数或返回值的动作运行 |                            |
| Supplier\<T>        | 无       | T        | get        | 提供一个 T 类型的值          |                            |
| Comsumer\<T>        | T        | void     | accept     | 处理一个 T 类型的值          | andThen                    |
| BiComsumer<T, U>    | T, U     | void     | accept     | 处理 T 和 U 类型的值         | andThen                    |
| Function<T, R>      | T        | R        | apply      | 有一个 T 类型参数的函数      | compose，andThen，identity |
| BiFunction<T, U, R> | T, U     | R        | apply      | 有 T 和 U 类型参数的函数     | andThen                    |
| UnaryOperator\<T>   | T        | T        | apply      | 类型 T 上的一元操作符        | compose，andThen，identity |
| BinaryOperator\<T,> | T, T     | T        | apply      | 类型 T 上的二元操作符        | andThen，maxBy，minBy      |
| Predicate\<T>       | T        | boolean  | test       | 布尔值函数                   | and，or，negate，isEqual   |
| BiPredicate<T, U>   | T, U     | boolean  | test       | 有两个参数的布尔值函数       | and，or，negate            |

## 方法引用

有时候，可能已经有现成的方法可以完成想要传递到其他代码的某个动作。比如，只要出现一个定时器事件就打印这个事件对象，为此可以调用：

```java
Timer t = new Timer(1000, event -> System.out.println(event));
```

这种情况下，可以直接把 println 方法传递到 Timer 构造器：

```java
Timer t = new Timer(1000, System.out::println);
```

表达式 System.out::println 是一个方法引用，它等价于 lambda 表达式 x-> System.out.println(x) 。

方法引用要用 `::` 操作符分隔方法名与对象或类名，主要有 3 种情况：

- *object::instanceMethod*
- *Class::staticMethod*
- *Class::instanceMethod*

前 2 种情况，方法引用等价于提供方法参数的 lambda 表达式。System.out::println 等价于 x -> System.out.println(x) 。类似地，Math::pow 等价于 (x, y) -> Math.pow(x, y) 。

第 3 种情况，第一个参数会成为方法的目标。例如，String::compareToIgnoreCase 等同于 (x, y) -> x.compareToIgnoreCase(y);

可以在方法引用中使用 this 参数。例如，this::equals 等同于 x -> this.equals(x) 。使用 super 也是合法的。

## 构造器引用

构造器引用与方法引用类似，只不过方法名为 new 。假设有一个字符串列表，可以把它转化为一个 Person 对象数组：

```java
ArrayList<Person> names = ...;
Stream<Person> stream = names.stream().map(Person::new);
List<Person> people = stream.collect(Collectors.toList());
```

map 方法会为各个元素调用 Person(String) 构造器。

可以用数组类型建立构造器引用，例如，int[]::new 是一个构造器引用，它等同于 x -> new int[x] 。

> Java 有一个限制，无法构造泛型类型 T 的数组，表达式 new T[n] 会出现错误。Stream 接口有一个 toArray 方法可以返回 Object 数组：Object[] people = stream.toArray() ，如果希望得到一个 Person 数组，可以使用构造器引用：People[] people = stream.toArray(Person::new) 。

