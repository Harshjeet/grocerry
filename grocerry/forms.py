from flask_wtf import FlaskForm
from wtforms import StringField, FloatField, FileField, SelectField, TextAreaField, DateField, IntegerField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, ValidationError
from flask_wtf.file import FileAllowed

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

class ProductForm(FlaskForm):
    name = StringField(
        'Product Name',
        validators=[
            DataRequired(message="Product name is required."),
            Length(max=100, message="Product name must not exceed 100 characters.")
        ]
    )
    price = FloatField(
        'Price',
        validators=[
            DataRequired(message="Price is required."),
            NumberRange(min=0, message="Price must be a positive value.")
        ]
    )
    image = FileField(
        'Product Image',
        validators=[
            FileAllowed(ALLOWED_EXTENSIONS, message="Only image files (png, jpg, jpeg, gif) are allowed."),
            Optional()  
        ]
    )
    category = SelectField(
        'Category',
        choices=[],
        validators=[
            DataRequired(message="Category is required.")
        ]
    )
    description = TextAreaField(
        'Description',
        validators=[
            DataRequired(message="Description is required."),
            Length(max=500, message="Description must not exceed 500 characters.")
        ]
    )
    edit_image = FileField(
        'Edit Product Image',
        validators=[
            FileAllowed(ALLOWED_EXTENSIONS, message="Only image files (png, jpg, jpeg, gif) are allowed."),
            Optional() 
        ]
    )
    manufacture_date = DateField(
        'Manufacture Date',
        validators=[Optional()],
        format='%Y-%m-%d'  
    )
    expiry_date = DateField(
        'Expiry Date',
        validators=[Optional()],
        format='%Y-%m-%d' 
    )
    quantity = IntegerField(
        'Quantity',
        validators=[
            DataRequired(message="Quantity is required."),
            NumberRange(min=0, message="Quantity must be a positive integer.")
        ]
    )

    def validate_expiry_date(self, field):
        """Custom validator to ensure expiry date is after manufacture date."""
        if self.manufacture_date.data and field.data and field.data <= self.manufacture_date.data:
            raise ValidationError("Expiry date must be after the manufacture date.")

    @staticmethod
    def set_category_choices(categories):
        """Dynamically set choices for the category field."""
        choices = [(category.id, category.name) for category in categories]
        return choices
