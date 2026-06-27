# src/patterns/singleton.py

class SingletonMeta(type):
    """
    Patrón Creacional: Singleton.
    Garantiza que solo exista una instancia de la clase que lo implemente.
    Ideal para gestionar la conexión a la base de datos de forma segura y centralizada.
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]