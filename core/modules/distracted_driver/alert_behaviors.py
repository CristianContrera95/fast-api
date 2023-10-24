from enum import Enum


class AlertBehaviors(str, Enum):
    safe = "safe"
    unsafe = "unsafe"
    single_hand = "single_hand"
    eating_drinking = "eating_drinking"
    tamper = "tamper"