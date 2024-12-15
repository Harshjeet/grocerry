from flask import Blueprint, request, jsonify
from flask_restful import Resource, Api
from marshmallow import Schema, fields, ValidationError
from .models import Product, Category
from . import db

api_bp = Blueprint('api', __name__)
api = Api(api_bp)

# Schemas for Validation
class ProductSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str()
    category = fields.Str(required=True)
    price = fields.Float(required=True)
    quantity = fields.Int(required=True)
    manufacture_date = fields.Date()
    expiry_date = fields.Date()
    image = fields.Str()

class CategorySchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)

# Instantiate schemas
product_schema = ProductSchema()
products_schema = ProductSchema(many=True)
category_schema = CategorySchema()
categories_schema = CategorySchema(many=True)


# Product Resource
class ProductResource(Resource):
    def get(self, product_id=None):
        try:
            if product_id:
                product = Product.query.get(product_id)
                if product:
                    return product_schema.dump(product), 200
                return {"message": "Product not found"}, 404

            products = Product.query.all()
            return products_schema.dump(products), 200
        except Exception as e:
            return {"message": "Error fetching products", "error": str(e)}, 500

    def post(self):
        try:
            data = request.json
            product_data = product_schema.load(data)  # Validate input
            product = Product(**product_data)
            db.session.add(product)
            db.session.commit()
            return product_schema.dump(product), 201
        except ValidationError as err:
            return {"message": "Invalid data", "errors": err.messages}, 400
        except Exception as e:
            return {"message": "Error creating product", "error": str(e)}, 500

    def put(self, product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"message": "Product not found"}, 404

            data = request.json
            product_data = product_schema.load(data, partial=True)  # Allow partial updates
            for key, value in product_data.items():
                setattr(product, key, value)
            db.session.commit()
            return product_schema.dump(product), 200
        except ValidationError as err:
            return {"message": "Invalid data", "errors": err.messages}, 400
        except Exception as e:
            return {"message": "Error updating product", "error": str(e)}, 500

    def delete(self, product_id):
        try:
            product = Product.query.get(product_id)
            if not product:
                return {"message": "Product not found"}, 404

            db.session.delete(product)
            db.session.commit()
            return {"message": "Product deleted successfully"}, 204
        except Exception as e:
            return {"message": "Error deleting product", "error": str(e)}, 500


# Category Resource
class CategoryResource(Resource):
    def get(self, category_id=None):
        try:
            if category_id:
                category = Category.query.get(category_id)
                if category:
                    return category_schema.dump(category), 200
                return {"message": "Category not found"}, 404

            categories = Category.query.all()
            return categories_schema.dump(categories), 200
        except Exception as e:
            return {"message": "Error fetching categories", "error": str(e)}, 500

    def post(self):
        try:
            data = request.json
            category_data = category_schema.load(data)  # Validate input
            category = Category(**category_data)
            db.session.add(category)
            db.session.commit()
            return category_schema.dump(category), 201
        except ValidationError as err:
            return {"message": "Invalid data", "errors": err.messages}, 400
        except Exception as e:
            return {"message": "Error creating category", "error": str(e)}, 500

    def put(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return {"message": "Category not found"}, 404

            data = request.json
            category_data = category_schema.load(data, partial=True)  # Allow partial updates
            for key, value in category_data.items():
                setattr(category, key, value)
            db.session.commit()
            return category_schema.dump(category), 200
        except ValidationError as err:
            return {"message": "Invalid data", "errors": err.messages}, 400
        except Exception as e:
            return {"message": "Error updating category", "error": str(e)}, 500

    def delete(self, category_id):
        try:
            category = Category.query.get(category_id)
            if not category:
                return {"message": "Category not found"}, 404

            db.session.delete(category)
            db.session.commit()
            return {"message": "Category deleted successfully"}, 204
        except Exception as e:
            return {"message": "Error deleting category", "error": str(e)}, 500


# Add resources to the API
api.add_resource(ProductResource, '/api/products', '/api/products/<int:product_id>')
api.add_resource(CategoryResource, '/api/categories', '/api/categories/<int:category_id>')
