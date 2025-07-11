"""
Purchase Orders models for ProjectMeats.

Migrated from PowerApps entity: pro_purchaseorder
Original description: "This table contains records of purchase orders including item details and supplier information."

PowerApps Entity Name: pro_PurchaseOrder
Django Model Name: PurchaseOrder
"""
from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from apps.core.models import OwnedModel, StatusModel


class PurchaseOrder(OwnedModel, StatusModel):
    """
    Purchase Order entity migrated from PowerApps pro_purchaseorder.

    PowerApps Field Mappings:
    - pro_po_number -> po_number (Primary field for display)
    - pro_item -> item (Item description)
    - pro_quantity -> quantity (Quantity ordered)
    - pro_priceperunit -> price_per_unit (Unit price as decimal)
    - pro_purchasedate -> purchase_date (Date of purchase)
    - pro_fulfillmentdate -> fulfillment_date (Expected fulfillment date)
    - pro_customer_lookup -> customer (foreign key)
    - pro_supplier_lookup -> supplier (foreign key)
    - pro_customerdocuments -> customer_documents (Customer document references)
    - pro_supplierdocuments -> supplier_documents (Supplier document references)
    + Standard PowerApps audit fields via OwnedModel base class
    """

    # Primary display field - equivalent to pro_po_number
    po_number = models.CharField(
        max_length=100, help_text="Equivalent to PowerApps pro_po_number field (Purchase Order Number)"
    )

    # Item details - equivalent to pro_item
    item = models.CharField(max_length=500, help_text="Equivalent to PowerApps pro_item field (Item description)")

    # Quantity - equivalent to pro_quantity
    quantity = models.IntegerField(
        validators=[MinValueValidator(1)], help_text="Equivalent to PowerApps pro_quantity field (Quantity ordered)"
    )

    # Price per unit - equivalent to pro_priceperunit (money type in PowerApps)
    price_per_unit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01"))],
        help_text="Equivalent to PowerApps pro_priceperunit field (Unit price)",
    )

    # Purchase date - equivalent to pro_purchasedate
    purchase_date = models.DateTimeField(help_text="Equivalent to PowerApps pro_purchasedate field (Date of purchase)")

    # Fulfillment date - equivalent to pro_fulfillmentdate
    fulfillment_date = models.DateTimeField(
        blank=True, null=True, help_text="Equivalent to PowerApps pro_fulfillmentdate field (Expected fulfillment date)"
    )

    # Foreign key relationships - equivalent to PowerApps lookup fields
    customer = models.ForeignKey(
        "customers.Customer",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        help_text="Equivalent to PowerApps pro_customer_lookup field",
    )

    supplier = models.ForeignKey(
        "suppliers.Supplier",
        on_delete=models.PROTECT,
        related_name="purchase_orders",
        help_text="Equivalent to PowerApps pro_supplier_lookup field",
    )

    # Location fields for plant-to-plant shipping
    origin_location = models.ForeignKey(
        "plants.Plant",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="outbound_purchase_orders",
        help_text="Origin plant location (typically from supplier's plants)",
    )

    end_location = models.ForeignKey(
        "plants.Plant",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="inbound_purchase_orders",
        help_text="Destination plant location",
    )

    # Document uploads - equivalent to pro_customerdocuments and pro_supplierdocuments
    # Changed from CharField to FileField to support actual file uploads
    customer_documents = models.FileField(
        upload_to="purchase_orders/customer_documents/",
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_customerdocuments field (Customer document uploads)",
    )

    supplier_documents = models.FileField(
        upload_to="purchase_orders/supplier_documents/",
        blank=True,
        null=True,
        help_text="Equivalent to PowerApps pro_supplierdocuments field (Supplier document uploads)",
    )

    class Meta:
        db_table = "purchase_orders_purchaseorder"
        verbose_name = "Purchase Order"
        verbose_name_plural = "Purchase Orders"
        ordering = ["-purchase_date", "po_number"]
        indexes = [
            models.Index(fields=["po_number"]),
            models.Index(fields=["purchase_date"]),
            models.Index(fields=["status"]),
            models.Index(fields=["customer"]),
            models.Index(fields=["supplier"]),
            models.Index(fields=["origin_location"]),
            models.Index(fields=["end_location"]),
        ]

    def __str__(self):
        """String representation using PO number and item."""
        return f"PO-{self.po_number}: {self.item}"

    def clean(self):
        """Model validation."""
        from django.core.exceptions import ValidationError

        errors = {}

        if not self.po_number or not self.po_number.strip():
            errors["po_number"] = "Purchase Order Number is required (PowerApps required field)"

        if not self.item or not self.item.strip():
            errors["item"] = "Item description is required"

        if self.fulfillment_date and self.purchase_date:
            if self.fulfillment_date < self.purchase_date:
                errors["fulfillment_date"] = "Fulfillment date cannot be before purchase date"

        if errors:
            raise ValidationError(errors)

    @property
    def total_amount(self):
        """Calculate total amount for this purchase order."""
        return self.quantity * self.price_per_unit

    @property
    def is_fulfilled(self):
        """Check if purchase order is past fulfillment date."""
        from django.utils import timezone

        if not self.fulfillment_date:
            return False
        return timezone.now().date() >= self.fulfillment_date.date()

    @property
    def has_documents(self):
        """Helper property to check if any documents are uploaded."""
        return bool(
            (self.customer_documents and self.customer_documents.name)
            or (self.supplier_documents and self.supplier_documents.name)
        )

    @classmethod
    def get_powerapps_entity_name(cls):
        """Returns the original PowerApps entity name for reference."""
        return "pro_purchaseorder"
