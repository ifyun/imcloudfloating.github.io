---
title: Java HashMap
date: 2019-09-26 22:00 +0800
categories: [Java, 集合框架]
tags: [Java, 集合框架]
seo:
  date_modified: 2019-10-20 19:07:12 +0800

---

HashMap 使用数组、链表和红黑树存储键值对，当链表足够长时，会转换为红黑树。HashMap 是非线程安全的。

## HashMap 中的常量

```java
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4;
static final int MAXIMUM_CAPACITY = 1 << 30;
static final float DEFAULT_LOAD_FACTOR = 0.75f;
static final int TREEIFY_THRESHOLD = 8;
static final int UNTREEIFY_THRESHOLD = 6;
static final int MIN_TREEIFY_CAPACITY = 64;
```

- `DEFAULT_INITIAL_CAPACITY`：初始容量为 16。
- `MAXIMUM_CAPACITY`：最大容量为 2<sup>30</sup> 。
- `DEFAULT_LOAD_FACTOR`：默认装填因子。初始情况下，当键值对数量大于 16 * 装填因子时，就会扩容为原来的 2 倍。
- `TREEIFY_THRESHOLD`：当链表的长度达到该值时，有可能会转化为树。
- `UNTREEIFY_THRESHOLD`：当链表长度小于该值时，会从树退化为链表。
- `MIN_TREEIFY_CAPACITY`：最小树化容量阈值，只有数组的容量大于该值时，才会转化为红黑树，若小于该值，只触发扩容。

> HashMap 中的容量用到了移位操作，将一个数 a 左移 n 位相当于：a = a * 2<sup>n</sup> ，所以 1 << 4 => 1 * 2<sup>4</sup> = 16 。因此，HashMap 的容量总是 2 的整数次幂。

使用有参构造方法可以指定初始容量和装填因子，指定的容量会被向上调整为 2 的整数次幂（比如给定容量为13，则会调整为 16）。

HashMap 中键值对的值可以为 null，可以存在一个 key 为 null 的键值对。

## 结构与容量调整

### tableSizeFor 方法

```java
/**
 * Returns a power of two size for the given target capacity.
 */
static final int tableSizeFor(int cap) {
    int n = cap - 1;
    n |= n >>> 1;
    n |= n >>> 2;
    n |= n >>> 4;
    n |= n >>> 8;
    n |= n >>> 16;
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```

该方法在使用构造方法指定容量时调用，返回一个大于 cap 的 2 的整数次幂的最小数。移位运算一共向右移动 31 位。

### treeifyBin 方法

```java
/**
 * Replaces all linked nodes in bin at index for given hash unless
 * table is too small, in which case resizes instead.
 */
final void treeifyBin(Node<K,V>[] tab, int hash) {
    int n, index; Node<K,V> e;
    // 判断是否达到转化为树的阈值
    if (tab == null || (n = tab.length) < MIN_TREEIFY_CAPACITY)
        resize();	// 没有达到只做扩容操作
    else if ((e = tab[index = (n - 1) & hash]) != null) {
        TreeNode<K,V> hd = null, tl = null;
        do {
            TreeNode<K,V> p = replacementTreeNode(e, null);
            if (tl == null)
                hd = p;
            else {
                p.prev = tl;
                tl.next = p;
            }
            tl = p;
        } while ((e = e.next) != null);
        if ((tab[index] = hd) != null)
            hd.treeify(tab);
    }
}
```

在调用 `put` 方法添加键值对时，如果数量达到了 `TREEIFY_THRESHOLD` ，就会调用 `treeifyBin` 方法，该方法会再判断一次数组的容量是否达到 `MIN_TREEIFY_CAPACITY`，如果没有达到，就只做扩容操作，否则将表转化为树。

这里的 (n - 1) & hash 就是求余操作，相当于 hash % n，效率更高。只有当 n 为 2 的整数次幂时才可以这样运算，这也是为什么 HashMap 的长度总是 2 的 n 次幂。

## 函数式接口方法

### replaceAll 方法

```java
@Override
public void replaceAll(BiFunction<? super K, ? super V, ? extends V> function) {
    Node<K,V>[] tab;
    if (function == null)
        throw new NullPointerException();
    if (size > 0 && (tab = table) != null) {
        int mc = modCount;
        for (int i = 0; i < tab.length; ++i) {
            for (Node<K,V> e = tab[i]; e != null; e = e.next) {
                e.value = function.apply(e.key, e.value);
            }
        }
        if (modCount != mc)
            throw new ConcurrentModificationException();
    }
}
```

该方法接受一个 `BiFunction` ，将满足给定条件的值替换掉：

```java
HashMap<Integer, String> map = ...;
// 将 key 为偶数的所有键值对的值替换为 "foo"
map.replaceAll((k, v) -> k % 2 == 0 ? "foo" : v);
```

### forEach 方法

```java
@Override
public void forEach(BiConsumer<? super K, ? super V> action) {
    Node<K,V>[] tab;
    if (action == null)
        throw new NullPointerException();
    if (size > 0 && (tab = table) != null) {
        int mc = modCount;
        for (int i = 0; i < tab.length; ++i) {
            for (Node<K,V> e = tab[i]; e != null; e = e.next)
                action.accept(e.key, e.value);
        }
        if (modCount != mc)
            throw new ConcurrentModificationException();
    }
}
```

该方法接受一个 `BiConsumer` ，根据指定的规则消费键值对：

```java
// 打印所有键值对
map.forEach(
    (k, v) -> System.out.println(k + ": " + v)
);

// 打印所有 key 为偶数的键值对
map.forEach(
    (k, v) -> {
        if (k % 2 == 0)
            System.out.println(k + ": " + v)
    }
);
```
