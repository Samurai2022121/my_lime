from haystack import indexes

from .models import LegalEntities, Shop, Supplier, Warehouse, WarehouseOrder


class LegalEntityIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)

    def get_model(self):
        return LegalEntities


class ShopIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)

    def get_model(self):
        return Shop


class SupplierIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)

    def get_model(self):
        return Supplier


class WarehouseIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)
    shop = indexes.IntegerField(model_attr="shop_id")

    def get_model(self):
        return Warehouse


class WarehouseOrderIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.NgramField(document=True, use_template=True)

    def get_model(self):
        return WarehouseOrder
