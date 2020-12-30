from django.db import models
from django.core.exceptions import ObjectDoesNotExist

# create a custom field that inherits from positive Integer Fields
# it will provide additional behavior 
# order object with respect to other fields 
# automatically assign an order value when no specific order is provided

class OrderField(models.PositiveIntegerField):
    
    # my order filed take optional for_fields parametter that to indicate the fields that 
    # the order has to be calculated with respect to  
    def __init__(self, for_fields=None, *args, **kwargs):
        self.for_fields = for_fields
        super(OrderField, self).__init__(*args, **kwargs)
    
    def pre_save(self, model_instance, add):
        # before saveing we check if a value already exist 
        if getattr(model_instance, self.attname) is None:
            # no current value
            try:
                # i build a query set to retrive object for the fields model 
                qs = self.model.objects.all()
                if self.for_fields:
                    # filter by object with the same field value for the fields in  "for_fields"
                    query = {field: getattr(model_instance, field) for field in self.for_fields}
                    # i retrive the object with highest order with last item from the database
                    qs = qs.filter(**query)
                # get the order from the last item
                last_item = qs.latest(self.attname)
                value = last_item.order + 1 
            except ObjectDoesNotExist:
                # if no object is found we assume that this object is the last one and assigned the order 'o'
                # if found we assigned '1' to the highest order found.
                value = 0 
            # we assigned the calculated order
            setattr(model_instance, self.attname, value)
            return value
        else:
            # if modeld instance has a value to the current field we don't do anything
            return super(OrderField, self).pre_save(model_instance, add)