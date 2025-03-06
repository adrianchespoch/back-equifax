class BaseRepository:
    # constructor: inject the model
    def __init__(self, model):
        self.model = model

    def find_all(self, order_by="id"):
        queryset = self.model.objects.all()
        if order_by:
            queryset = queryset.order_by(order_by)
        return queryset

    def find_one(self, pk) -> object | None:
        return self.model.objects.filter(pk=pk).first()

    def create(self, data) -> object:
        return self.model.objects.create(**data)

    def update(self, instance_id, data) -> object:
        instance = self.model.objects.get(pk=instance_id)
        for key, value in data.items():
            setattr(instance, key, value)
        instance.save()
        return instance

    def delete(self, instance_id) -> bool:
        instance = self.model.objects.filter(pk=instance_id).first()
        if not instance:
            return False
        instance.delete()
        return True
