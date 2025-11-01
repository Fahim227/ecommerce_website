from .models import Category, StoreConfig

def categories_processor(request):
    return {
        'categories': Category.objects.all()
    }

def store_config(request):
    config = StoreConfig.objects.first()
    return {"store_config": config}
