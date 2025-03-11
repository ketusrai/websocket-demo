from functools import lru_cache


class register:
    def __init__(self, cls, maxsize=2):
        self._cls = cls
        # 使用 lru_cache 装饰 _create_instance 方法，缓存最多 maxsize 个实例
        self._create_instance = lru_cache(maxsize=maxsize)(self._create_instance)

    def _create_instance(self, *args, **kwargs):
        instance = self._cls(*args, **kwargs)
        return instance

    def __call__(self, *args, **kwargs):
        return self._create_instance(*args, **kwargs)


@register
class MyClass:
    def __init__(self, value):
        self.value = value
        # 为了观察实例何时被创建，打印创建时的信息
        print(f"Creating instance for value = {value}")

    def display(self):
        print("Instance value:", self.value)


if __name__ == '__main__':
    # 创建两个实例，缓存中存放的是 key=(1,) 和 key=(2,)
    inst1 = MyClass(1)  # 输出 "Creating instance for value = 1"
    inst2 = MyClass(2)  # 输出 "Creating instance for value = 2"

    # 对 inst1 的参数再次调用，这会命中缓存，inst1 本身不会重新创建
    inst1_again = MyClass(1)  # 没有输出，因为从缓存中取出
    # 此时缓存中的两个键为：(1,) 和 (2,)
    # 下面创建一个新的实例，当传入不同参数时，缓存需要增加一项，
    # 此时超过 maxsize=2，LRU 策略会淘汰最久未使用的实例
    inst3 = MyClass(3)  # 输出 "Creating instance for value = 3"
    # 根据 lru_cache 的内部策略，此时在缓存中很可能淘汰掉 inst2 对应的 key (2,)
    # 具体淘汰哪个取决于调用顺序和缓存内部更新机制，
    # 但我们可以通过下面测试验证
    # 再次使用参数 2，查看是否重新创建一个新的实例
    inst2_again = MyClass(2)
    # 如果 inst2 对应的缓存项被淘汰，则会输出 "Creating instance for value = 2"，
    # 并且 inst2_again 与之前的 inst2 不再是同一个对象。
    print("inst1 is inst1_again:", inst1 is inst1_again)  # True，从缓存中取出同一个实例
    print("inst2 is inst2_again:", inst2 is inst2_again)  # 可能为 False，如果 inst2 被淘汰
    print("inst1 is inst3:", inst1 is inst3)  # False，参数不同
    # 调用 display 方法，验证各实例内容
    inst1.display()
    inst2.display()  # 可能为旧的，也可能 inst2_again（新创建）的值
    inst3.display()
