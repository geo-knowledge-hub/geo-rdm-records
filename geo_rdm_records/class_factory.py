# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Geo Secretariat.
#
# geo-rdm-records is free software; you can redistribute it and/or modify it
# under the terms of the MIT License; see LICENSE file for more details.

"""GEO RDM Records Object factory."""


class ClassFactory:
    """Factory class to generate object from different classes."""

    _factories = {}

    @classmethod
    def register(cls, name, factory):
        """Register a class in the factory."""
        cls._factories[name] = factory

    @classmethod
    def exists(cls, name):
        """Check if a class exists in the factory."""
        return name in cls._factories

    @classmethod
    def resolve(cls, datatype):
        """Resolve a string to a valid class type."""
        if cls.exists(datatype):
            return cls._factories[datatype]
        raise NotImplementedError(f"Factory for {datatype} is not implemented.")


def init_class_factory(factory, classes):
    """Helper function to register the classes in the Class Factory.

    Args:
        factory (ClassFactory): ClassFactory class.
        classes (List[object]): Classes to be registered in the Class Factory.
    """
    # Register each class in the factory.
    list(map(lambda cls: factory.register(cls.__name__, cls), classes))
