from .celery import celery_app	    # импорт приложение Celery в основной скрипт __init__.py проекта Django
__all__ = ('celery_app',)  		    # регистрация приложения Celery как символ пространства имен в пакете Django.
