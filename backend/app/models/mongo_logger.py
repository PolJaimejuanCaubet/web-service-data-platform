from datetime import datetime, timezone


class MongoLogger:

    SERVICES = {"UserService", "DataService"}
    STATUS = {"error", "success", "warning"}

    def __init__(self, collection):
        self._collection = collection

    async def log(self, service, status, message, metadata=None):

        if service not in self.SERVICES or status.lower() not in self.STATUS:
            raise ValueError(
                f"Your {service} or {status} must change to one on the following ones {self.SERVICES} | {self.STATUS}"
            )

        x = {
            "service": service,
            "status": status.lower(),
            "message": message,
            "metadata": metadata or {},
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        await self._collection.insert_one(x)
        return x
