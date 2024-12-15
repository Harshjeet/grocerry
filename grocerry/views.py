from flask import Blueprint, render_template, request, flash, redirect, url_for, current_app
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.utils import secure_filename
from sqlalchemy import or_
import os
import secrets
from datetime import datetime
from . import db
from .forms import ProductForm
from .models import Product, Order, OrderItem, User, Cart

views = Blueprint('views', __name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Helpers
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_images(image):
    """Save uploaded images securely and return the saved filename."""
    try:
        hash_photo = secrets.token_urlsafe(10)
        _, file_extension = os.path.splitext(image.filename)
        image_name = hash_photo + file_extension
        file_path = os.path.join(current_app.root_path, 'static/product_images', image_name)
        image.save(file_path)
        return image_name
    except Exception as e:
        flash("Error saving image. Please try again.", "error")
        return None


# Routes
@views.route('/')
@views.route('/home')
def home():
    return render_template('home.html')


@views.route('/admin-dashboard', methods=['GET'])
@login_required
def admin_dashboard():
    if current_user.role != 'adminRole':
        flash("Access restricted to admins only.", "error")
        return redirect(url_for('views.home'))
    try:
        products = Product.query.all()
        return render_template('admin_dashboard.html', name=current_user, products=products)
    except Exception as e:
        flash("Error fetching products. Please try again later.", "error")
        return redirect(url_for('views.home'))


@views.route('/add-product', methods=['GET', 'POST'])
@login_required
def add_product():
    if current_user.role != 'adminRole':
        flash("Access restricted to admins only.", "error")
        return redirect(url_for('views.home'))

    form = ProductForm()
    if form.validate_on_submit():
        try:
            image_name = save_images(form.image.data) if form.image.data else None
            product = Product(
                name=form.name.data,
                price=form.price.data,
                image=image_name,
                category=form.category.data,
                description=form.description.data,
                manufacture_date=form.manufacture_date.data,
                expiry_date=form.expiry_date.data
            )
            db.session.add(product)
            db.session.commit()
            flash("Product added successfully!", "success")
            return redirect(url_for('views.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("Error adding product. Please try again.", "error")

    return render_template('add_product.html', form=form)


@views.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    if current_user.role != 'adminRole':
        flash("Access restricted to admins only.", "error")
        return redirect(url_for('views.home'))

    product = Product.query.get_or_404(product_id)
    form = ProductForm(obj=product)

    if form.validate_on_submit():
        try:
            form.populate_obj(product)

            # Update image if provided
            if form.image.data and allowed_file(form.image.data.filename):
                image_name = save_images(form.image.data)
                product.image = image_name

            db.session.commit()
            flash("Product updated successfully!", "success")
            return redirect(url_for('views.admin_dashboard'))
        except Exception as e:
            db.session.rollback()
            flash("Error updating product. Please try again.", "error")

    return render_template('edit_product.html', form=form, product=product)


@views.route('/delete-product/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    if current_user.role != 'adminRole':
        flash("Access restricted to admins only.", "error")
        return redirect(url_for('views.home'))

    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        flash("Product deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting product. Please try again.", "error")
    return redirect(url_for('views.admin_dashboard'))


@views.route('/user-dashboard', methods=['GET'])
@login_required
def user_dashboard():
    try:
        products = Product.query.all()
        return render_template('user_dashboard.html', name=current_user, products=products)
    except Exception as e:
        flash("Error loading products. Please try again.", "error")
        return redirect(url_for('views.home'))


@views.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', default=1, type=int)

    try:
        product = Product.query.get_or_404(product_id)

        if product.quantity < quantity:
            flash("Not enough stock available.", "warning")
            return redirect(url_for('views.user_dashboard'))

        cart_item = Cart.query.filter_by(user_id=current_user.id, product_id=product_id).first()

        if cart_item:
            cart_item.quantity += quantity
            cart_item.total_price = cart_item.product.price * cart_item.quantity
        else:
            cart_item = Cart(
                user_id=current_user.id,
                product_id=product_id,
                quantity=quantity,
                total_price=product.price * quantity
            )
            db.session.add(cart_item)

        db.session.commit()
        flash("Product added to cart!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error adding product to cart. Please try again.", "error")

    return redirect(url_for('views.cart'))


@views.route('/cart', methods=['GET'])
@login_required
def cart():
    try:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()
        total_price = sum(item.product.price * item.quantity for item in cart_items)
        return render_template('cart.html', cart_items=cart_items, total_price=total_price)
    except Exception as e:
        flash("Error loading cart. Please try again.", "error")
        return redirect(url_for('views.user_dashboard'))


@views.route('/buy', methods=['POST'])
@login_required
def buy():
    try:
        cart_items = Cart.query.filter_by(user_id=current_user.id).all()

        if not cart_items:
            flash("Your cart is empty.", "warning")
            return redirect(url_for('views.cart'))

        total_amount = sum(item.total_price for item in cart_items)
        order = Order(user_id=current_user.id, order_date=datetime.utcnow(), total_amount=total_amount)

        db.session.add(order)

        for cart_item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                item_price=cart_item.product.price
            )
            db.session.add(order_item)
            db.session.delete(cart_item)

        db.session.commit()
        flash("Purchase successful!", "success")
        return redirect(url_for('views.order_history'))
    except Exception as e:
        db.session.rollback()
        flash("Error completing purchase. Please try again.", "error")
        return redirect(url_for('views.cart'))


@views.route('/order-history', methods=['GET'])
@login_required
def order_history():
    try:
        recent_purchases = OrderItem.query.join(Order).filter(Order.user_id == current_user.id).order_by(Order.order_date.desc()).all()
        return render_template('order_history.html', recent_purchases=recent_purchases)
    except Exception as e:
        flash("Error loading order history. Please try again.", "error")
        return redirect(url_for('views.home'))
