import enum

class BuddyStatus(str, enum.Enum):
    WAITING = "WAITING"
    MATCHED = "MATCHED"
    TIMED_OUT = "TIMED_OUT"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class OrderStatus(str, enum.Enum):
    CREATED = "CREATED"
    PAYMENT_PENDING = "PAYMENT_PENDING"
    PAYMENT_CONFIRMED = "PAYMENT_CONFIRMED"
    PREPARING = "PREPARING"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class DriverStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    INACTIVE = "INACTIVE"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class DeliveryStatus(str, enum.Enum):
    ASSIGNED = "ASSIGNED"
    IN_TRANSIT = "IN_TRANSIT"
    DELIVERED = "DELIVERED"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class PaymentMethod(str, enum.Enum):
    ONLINE = "ONLINE"
    COD = "COD"
    WALLET = "WALLET"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class PaymentStatus(str, enum.Enum):
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class CancellationReason(str, enum.Enum):
    PAYMENT_FAILED = "PAYMENT_FAILED"
    USER_WITHDREW = "USER_WITHDREW"
    TIMEOUT = "TIMEOUT"
    SYSTEM_ERROR = "SYSTEM_ERROR"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class TransactionType(str, enum.Enum):
    PAYMENT = "PAYMENT"
    REFUND = "REFUND"
    PENALTY = "PENALTY"
    COMPENSATION = "COMPENSATION"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")

class TransactionStatus(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    
    @classmethod
    def _missing_(cls, value):
        if isinstance(value, str):
            for member in cls:
                if member.value.lower() == value.lower():
                    return member
        raise ValueError(f"'{value}' is not a valid {cls.__name__}")
