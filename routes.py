"""
Routes module - Contains all application routes and logic
"""
from flask import render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from difflib import SequenceMatcher
from datetime import datetime
import jsonify
from models import User, LostItem,ResolvedMatch, FoundItem, db
from functools import wraps

# Categories for items
CATEGORIES = [
    'Électronique', 'Vêtements', 'Bijoux', 'Clés', 'Portefeuille/Sac',
    'Documents', 'Livres', 'Jouets', 'Lunettes', 'Autre'
]



def register_routes(app):
    """Register all routes with the Flask app."""
    
    @app.route('/')
    def home():
        """Home route - displays recent lost and found items."""
        try:
            # Debug the queries
            all_lost = LostItem.query.all()
            print(f"📊 Total lost items in DB: {len(all_lost)}")
            
            recent_lost_items = LostItem.query.filter_by(status='active').order_by(LostItem.date_posted.desc()).limit(6).all()
            recent_found_items = FoundItem.query.filter_by(status='active').order_by(FoundItem.date_posted.desc()).limit(6).all()
            
           
            
            return render_template('home.html', 
                                recent_lost_items=recent_lost_items,
                                recent_found_items=recent_found_items)
                                
        except Exception as e:
            print(f"❌ Error in home route: {e}")
            import traceback
            traceback.print_exc()
            
            # Return template with empty lists on error
            return render_template('home.html', 
                                recent_lost_items=[],
                                recent_found_items=[])
    def login_required(f):
        """Decorator to ensure user is logged in."""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Vous devez être connecté pour accéder à cette page.', 'error')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        """User registration."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            email = request.form.get('email', '').strip()
            
            # Validation
            if not username or not password:
                flash("Nom d'utilisateur et mot de passe requis", "error")
                return render_template('register.html')
            
            if len(password) < 6:
                flash("Le mot de passe doit contenir au moins 6 caractères", "error")
                return render_template('register.html')
            
            # Check if username exists
            if User.query.filter_by(username=username).first():
                flash("Nom d'utilisateur déjà pris", "error")
                return render_template('register.html')
            
            # Check if email exists (if provided)
            if email and User.query.filter_by(email=email).first():
                flash("Email déjà utilisé", "error")
                return render_template('register.html')
            
            # Create new user
            hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
            user = User(username=username, password=hashed_password, email=email or None)
            
            try:
                db.session.add(user)
                db.session.commit()
                flash("Inscription réussie ! Vous pouvez maintenant vous connecter.", "success")
                return redirect(url_for('login'))
            except Exception as e:
                db.session.rollback()
                flash("Erreur lors de l'inscription. Veuillez réessayer.", "error")
                return render_template('register.html')
        
        return render_template('register.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login."""
        if request.method == 'POST':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            
            if not username or not password:
                flash("Nom d'utilisateur et mot de passe requis", "error")
                return render_template('login.html')
            
            user = User.query.filter_by(username=username).first()
            
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                flash(f"Bienvenue, {user.username} !", "success")
                return redirect(url_for('home'))
            
            flash("Identifiants incorrects", "error")
        
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        """User logout."""
        username = session.get('username', 'Utilisateur')
        session.clear()
        flash(f"Au revoir, {username} !", "info")
        return redirect(url_for('home'))

    @app.route('/dashboard')
    def dashboard():  # Remove @login_required temporarily for debugging
        """Simplified dashboard route for debugging"""
        print("📊 Dashboard route called")
        
        try:
            # Check session
            if 'user_id' not in session:
                print("❌ No user_id in session")
                print(f"Session contents: {dict(session)}")
                flash("Vous devez être connecté pour accéder au tableau de bord.", "error")
                return redirect(url_for('login'))
            
            user_id = session['user_id']
            print(f"✅ User ID from session: {user_id}")
            
            # Simple queries
            user_lost_items = LostItem.query.filter_by(user_id=user_id).all()
            user_found_items = FoundItem.query.filter_by(user_id=user_id).all()
            
            print(f"📦 User has {len(user_lost_items)} lost items")
            print(f"🎯 User has {len(user_found_items)} found items")
            
            # Simple stats
            total_lost = len(user_lost_items)
            total_found = len(user_found_items)
            active_lost = len([item for item in user_lost_items if item.status == 'active'])
            active_found = len([item for item in user_found_items if item.status == 'active'])
            resolved_items = total_lost + total_found - active_lost - active_found
            
            print(f"📊 Stats: Lost={total_lost}, Found={total_found}, ActiveLost={active_lost}, ActiveFound={active_found}")
            
            return render_template('dashboard.html',
                                user_lost_items=user_lost_items,
                                user_found_items=user_found_items,
                                total_lost=total_lost,
                                total_found=total_found,
                                active_lost=active_lost,
                                active_found=active_found,
                                resolved_items=resolved_items)
                                
        except Exception as e:
            print(f"❌ Dashboard error: {e}")
            import traceback
            traceback.print_exc()
            flash(f'Erreur: {str(e)}', 'error')
            return redirect(url_for('home'))

    #

    @app.route('/lost', methods=['GET', 'POST'])
    def lost():
        """Declare a lost item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté pour déclarer un objet perdu", "error")
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            location = request.form.get('location', '').strip()
            date_lost_str = request.form.get('date_lost', '').strip()
            contact_method = request.form.get('contact_method', 'email').strip()
            contact_info = request.form.get('contact_info', '').strip()
            reward = request.form.get('reward', '').strip()
            
            # Validation
            if not all([title, description, category, location, date_lost_str]):
                flash("Tous les champs obligatoires doivent être remplis", "error")
                return render_template('lost.html', categories=CATEGORIES)
            
            try:
                date_lost = datetime.strptime(date_lost_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Format de date invalide", "error")
                return render_template('lost.html', categories=CATEGORIES)
            
            # Create lost item
            lost_item = LostItem(
                title=title,
                description=description,
                category=category,
                location=location,
                date_lost=date_lost,
                contact_method=contact_method,
                contact_info=contact_info,
                reward=reward,
                user_id=session['user_id']
            )
            
            try:
                db.session.add(lost_item)
                db.session.commit()
                flash("Objet perdu déclaré avec succès !", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("Erreur lors de la déclaration. Veuillez réessayer.", "error")
        
        return render_template('lost.html', categories=CATEGORIES)

    @app.route('/found', methods=['GET', 'POST'])
    def found():
        """Declare a found item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté pour déclarer un objet retrouvé", "error")
            return redirect(url_for('login'))
        
        if request.method == 'POST':
            # Get form data
            title = request.form.get('title', '').strip()
            description = request.form.get('description', '').strip()
            category = request.form.get('category', '').strip()
            location = request.form.get('location', '').strip()
            date_found_str = request.form.get('date_found', '').strip()
            contact_method = request.form.get('contact_method', 'email').strip()
            contact_info = request.form.get('contact_info', '').strip()
            
            # Validation
            if not all([title, description, category, location, date_found_str]):
                flash("Tous les champs obligatoires doivent être remplis", "error")
                return render_template('found.html', categories=CATEGORIES)
            
            try:
                date_found = datetime.strptime(date_found_str, '%Y-%m-%d').date()
            except ValueError:
                flash("Format de date invalide", "error")
                return render_template('found.html', categories=CATEGORIES)
            
            # Create found item
            found_item = FoundItem(
                title=title,
                description=description,
                category=category,
                location=location,
                date_found=date_found,
                contact_method=contact_method,
                contact_info=contact_info,
                user_id=session['user_id']
            )
            
            try:
                db.session.add(found_item)
                db.session.commit()
                flash("Objet retrouvé déclaré avec succès !", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("Erreur lors de la déclaration. Veuillez réessayer.", "error")
        
        return render_template('found.html', categories=CATEGORIES)

    @app.route('/edit_lost/<int:item_id>', methods=['GET', 'POST'])
    def edit_lost(item_id):
        """Edit a lost item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté", "error")
            return redirect(url_for('login'))
        
        item = LostItem.query.get_or_404(item_id)
        
        if item.user_id != session['user_id']:
            flash("Vous ne pouvez modifier que vos propres objets", "error")
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Update item with form data
            item.title = request.form.get('title', '').strip()
            item.description = request.form.get('description', '').strip()
            item.category = request.form.get('category', '').strip()
            item.location = request.form.get('location', '').strip()
            item.contact_method = request.form.get('contact_method', 'email').strip()
            item.contact_info = request.form.get('contact_info', '').strip()
            item.reward = request.form.get('reward', '').strip()
            item.status = request.form.get('status', 'active').strip()
            
            date_lost_str = request.form.get('date_lost', '').strip()
            if date_lost_str:
                try:
                    item.date_lost = datetime.strptime(date_lost_str, '%Y-%m-%d').date()
                except ValueError:
                    flash("Format de date invalide", "error")
                    return render_template('edit_lost.html', item=item, categories=CATEGORIES)
            
            try:
                db.session.commit()
                flash("Objet perdu mis à jour avec succès !", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("Erreur lors de la mise à jour", "error")
        
        return render_template('edit_lost.html', item=item, categories=CATEGORIES)

    @app.route('/edit_found/<int:item_id>', methods=['GET', 'POST'])
    def edit_found(item_id):
        """Edit a found item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté", "error")
            return redirect(url_for('login'))
        
        item = FoundItem.query.get_or_404(item_id)
        
        if item.user_id != session['user_id']:
            flash("Vous ne pouvez modifier que vos propres objets", "error")
            return redirect(url_for('dashboard'))
        
        if request.method == 'POST':
            # Update item with form data
            item.title = request.form.get('title', '').strip()
            item.description = request.form.get('description', '').strip()
            item.category = request.form.get('category', '').strip()
            item.location = request.form.get('location', '').strip()
            item.contact_method = request.form.get('contact_method', 'email').strip()
            item.contact_info = request.form.get('contact_info', '').strip()
            item.status = request.form.get('status', 'active').strip()
            
            date_found_str = request.form.get('date_found', '').strip()
            if date_found_str:
                try:
                    item.date_found = datetime.strptime(date_found_str, '%Y-%m-%d').date()
                except ValueError:
                    flash("Format de date invalide", "error")
                    return render_template('edit_found.html', item=item, categories=CATEGORIES)
            
            try:
                db.session.commit()
                flash("Objet retrouvé mis à jour avec succès !", "success")
                return redirect(url_for('dashboard'))
            except Exception as e:
                db.session.rollback()
                flash("Erreur lors de la mise à jour", "error")
        
        return render_template('edit_found.html', item=item, categories=CATEGORIES)

    @app.route('/delete_lost/<int:item_id>')
    def delete_lost(item_id):
        """Delete a lost item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté", "error")
            return redirect(url_for('login'))
        
        item = LostItem.query.get_or_404(item_id)
        
        if item.user_id != session['user_id']:
            flash("Vous ne pouvez supprimer que vos propres objets", "error")
            return redirect(url_for('dashboard'))
        
        try:
            db.session.delete(item)
            db.session.commit()
            flash("Objet perdu supprimé avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de la suppression", "error")
        
        return redirect(url_for('dashboard'))

    @app.route('/delete_found/<int:item_id>')
    def delete_found(item_id):
        """Delete a found item."""
        if 'user_id' not in session:
            flash("Vous devez être connecté", "error")
            return redirect(url_for('login'))
        
        item = FoundItem.query.get_or_404(item_id)
        
        if item.user_id != session['user_id']:
            flash("Vous ne pouvez supprimer que vos propres objets", "error")
            return redirect(url_for('dashboard'))
        
        try:
            db.session.delete(item)
            db.session.commit()
            flash("Objet retrouvé supprimé avec succès !", "success")
        except Exception as e:
            db.session.rollback()
            flash("Erreur lors de la suppression", "error")
        
        return redirect(url_for('dashboard'))

    @app.route('/match')
    def match():
        """Find matches between lost and found items."""
        if 'user_id' not in session:
            flash("Vous devez être connecté pour voir les correspondances", "error")
            return redirect(url_for('login'))
        
        lost_items = LostItem.query.filter_by(status='active').all()
        found_items = FoundItem.query.filter_by(status='active').all()
        matches = []
        
        for lost in lost_items:
            for found in found_items:
                # Check category match first
                if lost.category == found.category:
                    # Calculate similarity
                    desc_similarity = SequenceMatcher(None, lost.description.lower(), found.description.lower()).ratio()
                    title_similarity = SequenceMatcher(None, lost.title.lower(), found.title.lower()).ratio()
                    
                    # Weighted average
                    final_similarity = (desc_similarity * 0.7) + (title_similarity * 0.3)
                    
                    if final_similarity > 0.5:  # Similarity threshold
                        matches.append((lost, found, final_similarity))
        
        # Sort by similarity (highest first)
        matches.sort(key=lambda x: x[2], reverse=True)
        
        return render_template('match.html', matches=matches)

    @app.route('/search')
    def search():
        """Search for items."""
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '').strip()
        
        # Base queries for active items only
        lost_items = LostItem.query.filter_by(status='active')
        found_items = FoundItem.query.filter_by(status='active')
        
        # Apply search filters
        if query:
            search_filter = f"%{query}%"
            lost_items = lost_items.filter(
                (LostItem.title.like(search_filter)) | 
                (LostItem.description.like(search_filter)) |
                (LostItem.location.like(search_filter))
            )
            found_items = found_items.filter(
                (FoundItem.title.like(search_filter)) | 
                (FoundItem.description.like(search_filter)) |
                (FoundItem.location.like(search_filter))
            )
        
        if category:
            lost_items = lost_items.filter_by(category=category)
            found_items = found_items.filter_by(category=category)
        
        # Execute queries
        lost_items = lost_items.order_by(LostItem.date_posted.desc()).all()
        found_items = found_items.order_by(FoundItem.date_posted.desc()).all()
        
        return render_template('search.html', 
                             lost_items=lost_items, 
                             found_items=found_items,
                             query=query,
                             category=category,
                             categories=CATEGORIES)
    

    @app.route('/api/get_contact_info', methods=['POST'])
    def get_contact_info():
        """Get contact information for users involved in a match"""
        try:
            data = request.get_json()
            lost_id = data.get('lost_id')
            found_id = data.get('found_id')
            
            if not lost_id or not found_id:
                return jsonify({'success': False, 'message': 'IDs manquants'})
            
            # Get the items and their users
            lost_item = LostItem.query.get(lost_id)
            found_item = FoundItem.query.get(found_id)
            
            if not lost_item or not found_item:
                return jsonify({'success': False, 'message': 'Objets non trouvés'})
            
            # Check if user is logged in
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Vous devez être connecté'})
            
            # Get contact information
            lost_user = lost_item.user
            found_user = found_item.user
            
            contact_info = {
                'success': True,
                'lost_item': {
                    'title': lost_item.title,
                    'user': lost_user.username,
                    'contact_method': lost_item.contact_method,
                    'contact_info': lost_item.contact_info,
                    'location': lost_item.location,
                    'date_lost': lost_item.date_lost.strftime('%d/%m/%Y')
                },
                'found_item': {
                    'title': found_item.title,
                    'user': found_user.username,
                    'contact_method': found_item.contact_method,
                    'contact_info': found_item.contact_info,
                    'location': found_item.location,
                    'date_found': found_item.date_found.strftime('%d/%m/%Y')
                }
            }
            
            return jsonify(contact_info)
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

    @app.route('/api/mark_resolved', methods=['POST'])
    def mark_resolved():
        """Mark a match as resolved"""
        try:
            data = request.get_json()
            lost_id = data.get('lost_id')
            found_id = data.get('found_id')
            notes = data.get('notes', '')
            
            if not lost_id or not found_id:
                return jsonify({'success': False, 'message': 'IDs manquants'})
            
            # Check if user is logged in
            if 'user_id' not in session:
                return jsonify({'success': False, 'message': 'Vous devez être connecté'})
            
            # Get the items
            lost_item = LostItem.query.get(lost_id)
            found_item = FoundItem.query.get(found_id)
            
            if not lost_item or not found_item:
                return jsonify({'success': False, 'message': 'Objets non trouvés'})
            
            # Check if user is involved in this match
            current_user_id = session['user_id']
            if (lost_item.user_id != current_user_id and 
                found_item.user_id != current_user_id):
                return jsonify({'success': False, 'message': 'Non autorisé'})
            
            # Check if already resolved
            existing_resolution = ResolvedMatch.query.filter_by(
                lost_item_id=lost_id,
                found_item_id=found_id
            ).first()
            
            if existing_resolution:
                return jsonify({'success': False, 'message': 'Déjà marqué comme résolu'})
            
            # Create resolution record
            resolution = ResolvedMatch(
                lost_item_id=lost_id,
                found_item_id=found_id,
                resolved_by_user_id=current_user_id,
                notes=notes
            )
            
            # Update item statuses
            lost_item.status = 'resolved'
            found_item.status = 'resolved'
            
            db.session.add(resolution)
            db.session.commit()
            
            return jsonify({
                'success': True, 
                'message': 'Correspondance marquée comme résolue avec succès!'
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({'success': False, 'message': f'Erreur: {str(e)}'})

    @app.route('/resolved_matches')
    @login_required
    def resolved_matches():
        """Show resolved matches for the current user"""
        user_id = session['user_id']
        
        # Get resolved matches where user was involved
        resolved = db.session.query(ResolvedMatch).join(
            LostItem, ResolvedMatch.lost_item_id == LostItem.id
        ).join(
            FoundItem, ResolvedMatch.found_item_id == FoundItem.id
        ).filter(
            db.or_(
                LostItem.user_id == user_id,
                FoundItem.user_id == user_id
            )
        ).order_by(ResolvedMatch.resolution_date.desc()).all()
        
        return render_template('resolved_matches.html', resolved_matches=resolved)


    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        flash("Page non trouvée", "error")
        return redirect(url_for('home'))

    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        db.session.rollback()
        flash("Erreur interne du serveur", "error")
        return redirect(url_for('home'))