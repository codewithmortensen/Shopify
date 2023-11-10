from rest_framework import serializers
from django.utils import timezone
from django.db import transaction
from . import models


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = [
            'customer_id', 'first_name', 'last_name', 'birth_date', 'phone',
            'email', 'membership', 'order_count'
        ]

    order_count = serializers.IntegerField(read_only=True)


class UpdateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['birth_date', 'phone']


class AdminUpdateCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['birth_date', 'phone', 'membership']


class SimpleProductSerializer(serializers.ModelSerializer):
    price = serializers.DecimalField(
        max_digits=6, decimal_places=3, source='new_price')

    class Meta:
        model = models.Product
        fields = ['id', 'title', 'price']


class CollectionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()
    featured_product = SimpleProductSerializer()
    products_count = serializers.IntegerField()

    class Meta:
        model = models.Collection
        fields = [
            'id', 'title', 'slug', 'featured_product',
            'promotion', 'products_count'
        ]


class CreateCollectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title', 'featured_product', 'promotion']


class PromotionSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(read_only=True)

    class Meta:
        model = models.Promotion
        fields = [
            'id', 'title', 'slug', 'description',
            'discount', 'start_date', 'end_date',
        ]

    now = timezone.now()

    def create(self, validated_data):

        start_date = validated_data['start_date']
        end_date = validated_data['end_date']

        errors = {}

        if start_date < self.now:
            errors['start_date'] = 'Start date cannot be in the past.'

        if end_date < self.now:
            errors['end_date'] = 'End date cannot be in the past.'

        if errors:
            raise serializers.ValidationError(errors)

        return super().create(validated_data)

    def update(self, instance: models.Promotion, validated_data):

        errors = {}

        if instance.start_date < self.now:
            errors['start_date'] = 'Start date cannot be in the past.'

        if instance.end_date < self.now:
            errors['end_date'] = 'End date cannot be in the past.'

        if errors:
            raise serializers.ValidationError(errors)

        return super().update(instance, validated_data)


class SimpleCollection(serializers.ModelSerializer):
    class Meta:
        model = models.Collection
        fields = ['id', 'title']


class SimplePromotionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Promotion
        fields = ['id', 'title', 'discount']


class ProductSerializer(serializers.ModelSerializer):
    slug = serializers.SlugField()
    collection = SimpleCollection()
    promotions = SimplePromotionSerializer(many=True)
    num_reviews = serializers.IntegerField()

    class Meta:
        model = models.Product
        fields = [
            'id', 'title', 'slug', 'description',
            'price', 'new_price', 'last_update',
            'collection', 'promotions', 'status', 'num_reviews', 'last_update', 'average_rating'
        ]

    status = serializers.SerializerMethodField(method_name='get_status')

    @staticmethod
    def get_status(product: models.Product):
        if not hasattr(product, 'stock') or product.stock.quantity_in_stock == 0:
            return {"in_stock": False, 'stock_level': None}

        out_put = 'Ok' if product.stock.quantity_in_stock > product.stock.threshold else 'Low'
        return {'in_stock': True, 'stock_level': out_put, 'stock': product.stock.quantity_in_stock}

    average_rating = serializers.SerializerMethodField(method_name='get_average_reviews')

    @staticmethod
    def get_average_reviews(product: models.Product):
        reviews = [float(review.rating) for review in product.reviews.all()]
        if len(reviews):
            average_review = sum(reviews) / len(reviews)
            rounded_average = min([1, 1.5, 2, 2.5, 3, 3.5, 4, 4.5, 5], key=lambda x: abs(x - average_review))
            return rounded_average
        return 0


class CreateProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Product
        fields = ['id', 'title', 'price',
                  'description', 'collection', 'promotions']


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ['product_id', 'quantity_in_stock', 'threshold']


class CreateStockSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stock
        fields = ['quantity_in_stock', 'threshold']

    def save(self, **kwargs):
        product_id = self.context['product_id']
        quantity = self.validated_data['quantity_in_stock']
        threshold = self.validated_data['threshold']
        try:
            stock = models.Stock.objects.get(product_id=product_id)
            stock.quantity_in_stock = quantity
            stock.threshold = threshold
            stock.save()
            self.instance = stock
        except models.Stock.DoesNotExist:
            self.instance = models.Stock.objects.create(
                product_id=product_id, **self.validated_data)
        return self.instance


class SimpleCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Customer
        fields = ['customer_id', 'first_name', 'last_name', 'membership']


class ReviewSerializer(serializers.ModelSerializer):
    customer = SimpleCustomerSerializer()

    class Meta:
        model = models.Review
        fields = [
            'id', 'customer', 'rating',
            'description', 'created_at', 'is_updated', 'updated_at'
        ]


class CreateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['id', 'rating', 'description']

    def create(self, validated_data):
        user_id = self.context['user_id']
        product_id = self.context['product_id']
        return models.Review.objects.create(customer_id=user_id, product_id=product_id, **validated_data)


class UpdateReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Review
        fields = ['rating', 'description']

    def update(self, instance: models.Review, validated_data):
        instance.is_updated = True
        instance.updated_at = timezone.now()
        instance.rating = validated_data.get('rating', instance.rating)
        instance.description = validated_data.get(
            'description', instance.description)

        return super().update(instance, validated_data)


class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()

    class Meta:
        model = models.CartItem
        fields = ['id', 'product', 'quantity', 'sub_total']

    sub_total = serializers.SerializerMethodField(method_name='get_sub_total')

    @staticmethod
    def get_sub_total(items: models.CartItem):
        return items.quantity * items.product.new_price


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Cart
        fields = ['id', 'created_at', 'items', 'total']

    total = serializers.SerializerMethodField(method_name='get_total')

    @staticmethod
    def get_total(cart: models.Cart):
        return sum([item.product.new_price * item.quantity for item in cart.items.all()])


class CreateCartItemSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField()

    @staticmethod
    def validate_product_id(product_id):
        product = models.Product.objects.filter(pk=product_id)
        if not product.exists():
            raise serializers.ValidationError(
                'Product with the Given ID does not exist')
        try:
            var: models.Stock = product.first().stock
            if var.quantity_in_stock <= 0:
                raise serializers.ValidationError('Error')
            return product_id

        except Exception:
            message = 'Product has no stock'
            raise serializers.ValidationError(message)

    class Meta:
        model = models.CartItem
        fields = ['product_id', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product_id']
        quantity = self.validated_data['quantity']

        try:
            stock = models.Stock.objects.get(pk=product_id)
            error = {'error': 'Quantity provided is greater than quantity in stock'}
            if quantity > stock.quantity_in_stock:
                raise serializers.ValidationError(error)

            items = models.CartItem.objects.get(
                cart_id=cart_id, product_id=product_id)
            items.quantity += quantity
            items.save()
            self.instance = items
        except models.CartItem.DoesNotExist:
            self.instance = models.CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance


class UpdateCartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CartItem
        fields = ['quantity']

    def update(self, instance: models.CartItem, validated_data):
        product_id = validated_data.get('product_id', instance.product.pk)

        quantity = validated_data.get('quantity', instance.quantity)
        stock = models.Stock.objects.get(pk=product_id)
        error = {'error': 'Quantity provided is greater than quantity in stock'}
        if stock.quantity_in_stock < quantity:
            raise serializers.ValidationError(error)

        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    customer = SimpleCustomerSerializer()
    item = CartItemSerializer(many=True)

    class Meta:
        model = models.Order
        fields = ['id', 'placed_at', 'order_status',
                  'payment_status', 'customer', 'item', 'total']

    total = serializers.SerializerMethodField(method_name='get_total')

    @staticmethod
    def get_total(order: models.Order):
        return sum([item.product.new_price * item.quantity for item in order.item.all()])


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    @staticmethod
    def validate_cart_id(cart_id):
        if not models.Cart.objects.filter(pk=cart_id).exists():
            raise serializers.ValidationError('Cart Does Not Exist')
        if models.CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Empty Cart')
        return cart_id

    def save(self, **kwargs):
        with (transaction.atomic()):
            cart = self.validated_data['cart_id']
            user_id = self.context['user_id']
            customer = models.Customer.objects.get(customer_id=user_id)
            order = models.Order.objects.create(customer=customer)

            cart_item = models.CartItem.objects.prefetch_related(
                'product').filter(cart=cart)
            items = [models.OrderItem(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.new_price)
                for item in cart_item
            ]

            models.OrderItem.objects \
                .select_related('product__collection__promotion') \
                .prefetch_related('product__collection__promotions') \
                .bulk_create(items)

            for instance in items:
                product_stock = instance.product.stock.quantity_in_stock
                quantity = instance.quantity
                if quantity > product_stock:
                    raise serializers.ValidationError(
                        {'error': 'Not enough instance of the product In stock'})

                models.Stock.objects.select_related('product').filter(product_id=instance.product.pk) \
                    .update(quantity_in_stock=product_stock - quantity)

            models.Cart.objects.filter(pk=cart).delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = ['order_status', 'payment_status']
