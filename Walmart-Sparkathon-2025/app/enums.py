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
    PREPARING = "PREPARING"
    DISPATCHED = "DISPATCHED"
    DELIVERED = "DELIVERED"
    
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
