# Generated by Django 4.0.1 on 2022-03-02 20:47

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

from internal_api.models import create_contract_download_path
from personnel.models import create_personnel_document_download_path


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("products", "0029_productunitconversion"),
    ]

    operations = [
        migrations.CreateModel(
            name="LegalEntities",
            fields=[
                (
                    "registration_id",
                    models.CharField(
                        max_length=9,
                        primary_key=True,
                        serialize=False,
                        verbose_name="регистрационный номер",
                    ),
                ),
                (
                    "registration_date",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="дата регистрации",
                    ),
                ),
                (
                    "active",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="действует"
                    ),
                ),
                (
                    "phone",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="телефон"
                    ),
                ),
                (
                    "region",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="регион"
                    ),
                ),
                (
                    "email",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="имейл"
                    ),
                ),
                (
                    "address",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="адрес"
                    ),
                ),
                (
                    "okved",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="ОКВЭД"
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="краткое наименование",
                    ),
                ),
                (
                    "full_name",
                    models.CharField(
                        blank=True,
                        max_length=255,
                        null=True,
                        verbose_name="полное наименование",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="статус"
                    ),
                ),
            ],
            options={
                "verbose_name": "Юридическое лицо",
                "verbose_name_plural": "Юридические лица",
                "db_table": "legal_entities",
                "managed": False,
            },
        ),
        migrations.CreateModel(
            name="Personnel",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("is_archived", models.BooleanField(default=False)),
                ("position", models.CharField(max_length=255)),
                (
                    "phone_number",
                    models.CharField(
                        max_length=17,
                        validators=[
                            django.core.validators.RegexValidator(
                                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.',
                                regex="^\\+?\\d{9,15}$",
                            )
                        ],
                    ),
                ),
                ("date_hired", models.DateTimeField(auto_now=True)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("working", "Работает"),
                            ("fired", "Уволен"),
                            ("vacation", "Отпуск"),
                            ("maternity_leave", "Декрет"),
                            ("probation", "Исп. срок"),
                        ],
                        max_length=255,
                    ),
                ),
                (
                    "photo",
                    models.ImageField(
                        blank=True, null=True, upload_to="internal-api/staff/"
                    ),
                ),
                ("first_name", models.CharField(max_length=255)),
                ("last_name", models.CharField(max_length=255)),
                ("fathers_name", models.CharField(max_length=255)),
                ("date_of_birth", models.DateField()),
                ("passport", models.CharField(max_length=100)),
                ("place_of_birth", models.CharField(max_length=255)),
                ("department_issued_passport", models.CharField(max_length=255)),
                ("identification_number", models.CharField(max_length=255)),
                ("date_passport_issued", models.DateField()),
                ("date_passport_valid", models.DateField()),
                ("contract_period", models.IntegerField()),
                ("contract_type", models.CharField(max_length=255)),
                ("is_archive", models.BooleanField(default=False)),
            ],
            options={
                "verbose_name": "Персонал",
                "verbose_name_plural": "Персонал",
            },
        ),
        migrations.CreateModel(
            name="PrimaryDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateField(auto_now_add=True, verbose_name="создан"),
                ),
                (
                    "number",
                    models.CharField(
                        blank=True, max_length=255, unique=True, verbose_name="номер"
                    ),
                ),
                (
                    "author",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ первичного учёта",
                "verbose_name_plural": "Документы первичного учёта",
                "ordering": ("created_at", "number"),
            },
        ),
        migrations.CreateModel(
            name="Shop",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("address", models.TextField()),
                ("name", models.CharField(max_length=255)),
                ("date_added", models.DateTimeField(auto_now=True)),
                ("is_archive", models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name="Supplier",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=255)),
                ("address", models.CharField(blank=True, max_length=255, null=True)),
                ("email", models.EmailField(blank=True, max_length=254, null=True)),
                (
                    "phone",
                    models.CharField(
                        blank=True,
                        max_length=17,
                        null=True,
                        validators=[
                            django.core.validators.RegexValidator(
                                message='Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.',
                                regex="^\\+?\\d{9,15}$",
                            )
                        ],
                    ),
                ),
                ("extra_info", models.JSONField(blank=True, null=True)),
                ("is_archive", models.BooleanField(default=False)),
                (
                    "bank_identifier_code",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                (
                    "bank_account",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("inner_id", models.CharField(blank=True, max_length=255, null=True)),
                (
                    "payer_identification_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
            options={
                "verbose_name": "Поставщик",
                "verbose_name_plural": "Поставщики",
            },
        ),
        migrations.CreateModel(
            name="Warehouse",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "min_remaining",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "max_remaining",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "margin",
                    models.DecimalField(
                        verbose_name="наценка, %",
                        blank=True,
                        decimal_places=2,
                        max_digits=4,
                        null=True,
                    ),
                ),
                ("auto_order", models.BooleanField(default=False)),
                (
                    "product_unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="products.productunit",
                    ),
                ),
                (
                    "shop",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="internal_api.shop",
                    ),
                ),
                (
                    "supplier",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="warehouse",
                        to="internal_api.supplier",
                    ),
                ),
            ],
            options={
                "verbose_name": "Запас",
                "verbose_name_plural": "Запасы",
                "default_related_name": "warehouses",
            },
        ),
        migrations.CreateModel(
            name="WarehouseOrder",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("approving", "Подтверждается"),
                            ("delivered", "Доставлен"),
                            ("canceled", "Отменен"),
                            ("dispatched", "Отправлен"),
                        ],
                        max_length=255,
                    ),
                ),
                ("waybill", models.CharField(blank=True, max_length=255, null=True)),
                ("waybill_date", models.DateField(blank=True, null=True)),
                (
                    "order_number",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
                ("is_archive", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={"verbose_name": "Заказ", "verbose_name_plural": "Заказы"},
        ),
        migrations.CreateModel(
            name="CancelDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="cancel_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
                (
                    "reason",
                    models.TextField(blank=True, null=True, verbose_name="причина"),
                ),
            ],
            options={
                "verbose_name": "Документ отмены",
                "verbose_name_plural": "Документы отмены",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="ConversionDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="conversion_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ перевода единиц хранения",
                "verbose_name_plural": "Документы перевода единиц хранения",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="InventoryDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="inventory_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Остаток на начало периода",
                "verbose_name_plural": "Остатки на начало периода",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="MoveDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="move_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ перемещения",
                "verbose_name_plural": "Документы перемещения",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="ProductionDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="production_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ учёта произведённой продукции",
                "verbose_name_plural": "Документы учёта произведённой продукции",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="SaleDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="sale_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ продажи",
                "verbose_name_plural": "Документы продажи",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="WriteOffDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="write_off_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
                (
                    "reason",
                    models.TextField(blank=True, null=True, verbose_name="причина"),
                ),
            ],
            options={
                "verbose_name": "Документ списания",
                "verbose_name_plural": "Документы списания",
            },
            bases=("internal_api.primarydocument",),
        ),
        migrations.CreateModel(
            name="WarehouseRecord",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "quantity",
                    models.DecimalField(
                        decimal_places=2, max_digits=7, verbose_name="количество"
                    ),
                ),
                (
                    "document",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="internal_api.primarydocument",
                        verbose_name="первичный документ",
                    ),
                ),
                (
                    "warehouse",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="internal_api.warehouse",
                        verbose_name="запас",
                    ),
                ),
            ],
            options={
                "verbose_name": "Изменение запаса",
                "verbose_name_plural": "Изменения запаса",
                "default_related_name": "warehouse_records",
            },
        ),
        migrations.CreateModel(
            name="WarehouseOrderPositions",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "quantity",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                ("bonus", models.IntegerField(default=0)),
                (
                    "special",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "flaw",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "buying_price",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "value_added_tax",
                    models.DecimalField(decimal_places=2, default=0, max_digits=4),
                ),
                (
                    "value_added_tax_value",
                    models.DecimalField(decimal_places=2, default=0, max_digits=7),
                ),
                (
                    "margin",
                    models.DecimalField(decimal_places=2, default=0, max_digits=4),
                ),
                (
                    "product_unit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="products.productunit",
                    ),
                ),
                (
                    "warehouse_order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="internal_api.warehouseorder",
                    ),
                ),
            ],
            options={
                "verbose_name": "Строка заказа",
                "verbose_name_plural": "Строки заказа",
                "default_related_name": "warehouse_order_positions",
            },
        ),
        migrations.AddField(
            model_name="warehouseorder",
            name="order_positions",
            field=models.ManyToManyField(
                blank=True,
                through="internal_api.WarehouseOrderPositions",
                to="products.ProductUnit",
            ),
        ),
        migrations.AddField(
            model_name="warehouseorder",
            name="shop",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="internal_api.shop"
            ),
        ),
        migrations.AddField(
            model_name="warehouseorder",
            name="supplier",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="warehouse_orders",
                to="internal_api.supplier",
            ),
        ),
        migrations.CreateModel(
            name="SupplyContract",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "contract",
                    models.FileField(upload_to=create_contract_download_path),
                ),
                ("contract_number", models.CharField(max_length=255)),
                ("contract_date", models.DateField()),
                (
                    "supplier",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="supply_contract",
                        to="internal_api.supplier",
                    ),
                ),
            ],
            options={
                "verbose_name": "Контракт поставщика",
                "verbose_name_plural": "Контракты поставщиков",
            },
        ),
        migrations.CreateModel(
            name="PersonnelDocument",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "personnel_document",
                    models.FileField(
                        null=True,
                        upload_to=create_personnel_document_download_path,
                    ),
                ),
                ("document_number", models.CharField(max_length=255)),
                ("document_date", models.DateField()),
                (
                    "personnel",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="personnel_document",
                        to="internal_api.personnel",
                    ),
                ),
            ],
            options={
                "abstract": False,
            },
        ),
        migrations.AddField(
            model_name="personnel",
            name="working_place",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="internal_api.shop"
            ),
        ),
        migrations.CreateModel(
            name="ReceiptDocument",
            fields=[
                (
                    "primary_document",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        parent_link=True,
                        primary_key=True,
                        related_name="receipt_document",
                        serialize=False,
                        to="internal_api.primarydocument",
                    ),
                ),
                (
                    "order",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="receipts",
                        to="internal_api.warehouseorder",
                        verbose_name="заказ",
                    ),
                ),
            ],
            options={
                "verbose_name": "Документ поступления товара",
                "verbose_name_plural": "Документы поступления товара",
            },
            bases=("internal_api.primarydocument",),
        ),
    ]
