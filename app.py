from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Context processor to make 'theme' available in all templates
@app.context_processor
def inject_global_data():
    conn = get_db_connection()
    try:
        # Theme
        theme_row = conn.execute("SELECT value FROM settings WHERE key = 'theme'").fetchone()
        theme = theme_row['value'] if theme_row else 'default'
        
        # Site Content
        site_rows = conn.execute("SELECT section, key, value FROM site_content WHERE page = 'global'").fetchall()
        site_data = {}
        for row in site_rows:
            if row['section'] not in site_data:
                site_data[row['section']] = {}
            site_data[row['section']][row['key']] = row['value']
            
    except sqlite3.OperationalError:
        theme = 'default'
        site_data = {}
    finally:
        conn.close()
    return dict(theme=theme, site=site_data)

def get_site_content(page):
    conn = get_db_connection()
    content_rows = conn.execute('SELECT section, key, value FROM site_content WHERE page = ?', (page,)).fetchall()
    conn.close()
    
    # Structure content as {section: {key: value}}
    structured = {}
    for row in content_rows:
        if row['section'] not in structured:
            structured[row['section']] = {}
        structured[row['section']][row['key']] = row['value']
    return structured

@app.route('/')
def index():
    content = get_site_content('home')
    return render_template('index.html', content=content)

@app.route('/how-it-works')
def how_it_works():
    conn = get_db_connection()
    steps = conn.execute('SELECT * FROM site_steps ORDER BY sort_order').fetchall()
    conn.close()
    return render_template('how_it_works.html', steps=steps)

@app.route('/features')
def features():
    conn = get_db_connection()
    features = conn.execute('SELECT * FROM site_features ORDER BY sort_order').fetchall()
    conn.close()
    return render_template('features.html', features=features)

@app.route('/roles')
def roles():
    conn = get_db_connection()
    roles_list = conn.execute('SELECT * FROM site_roles').fetchall()
    conn.close()
    
    # Process permissions back to lists
    processed_roles = []
    for r in roles_list:
        role_dict = dict(r)
        role_dict['permissions_list'] = r['permissions'].split(';')
        processed_roles.append(role_dict)
        
    return render_template('roles.html', roles=processed_roles)

@app.route('/tech-stack')
def tech_stack():
    conn = get_db_connection()
    tech_items = conn.execute('SELECT * FROM site_tech_stack').fetchall()
    conn.close()
    return render_template('tech_stack.html', tech_items=tech_items)

@app.route('/privacy')
def privacy():
    return render_template('privacy.html')

@app.route('/terms')
def terms():
    return render_template('terms.html')

@app.route('/contact', methods=('GET', 'POST'))
def contact():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        company = request.form.get('company')
        message = request.form['message']
        role = request.form['role']
        
        conn = get_db_connection()
        conn.execute('INSERT INTO contacts (name, email, company, message, role) VALUES (?, ?, ?, ?, ?)',
                     (name, email, company, message, role))
        conn.commit()
        conn.close()
        flash('Thank you for your message! We will get back to you soon.')
        return redirect(url_for('contact'))
        
    return render_template('contact.html')

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ? AND role = ?', (username, role)).fetchone()
        conn.close()
        
        if user and user['password'] == password:
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            if role == 'Admin':
                return redirect(url_for('admin_dashboard'))
            elif role == 'Project Supervisor':
                return redirect(url_for('portal_supervisor'))
            elif role == 'Marketing Team':
                return redirect(url_for('portal_marketing'))
            elif role == 'Content Creator':
                return redirect(url_for('portal_content'))
            elif role == 'Sales Team':
                return redirect(url_for('portal_sales'))
            else:
                return redirect(url_for('index'))
        else:
            flash('Invalid credentials. Please try again.')
    
    return render_template('login.html')

# --- Admin Routes ---

@app.route('/admin')
def admin_dashboard():
    conn = get_db_connection()
    try:
        user_count = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
        campaign_count = conn.execute('SELECT COUNT(*) FROM budget_requests WHERE status = "Approved"').fetchone()[0]
        contact_count = conn.execute('SELECT COUNT(*) FROM contacts').fetchone()[0]
        recent_contacts = conn.execute('SELECT * FROM contacts ORDER BY submitted_at DESC LIMIT 5').fetchall()
    except sqlite3.OperationalError:
        user_count = 0
        campaign_count = 0
        contact_count = 0
        recent_contacts = []
    finally:
        conn.close()
        
    return render_template('admin/dashboard.html', user_count=user_count, campaign_count=campaign_count, contact_count=contact_count, recent_contacts=recent_contacts)

@app.route('/admin/messages')
def admin_messages():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE receiver_role = "Admin" OR sender_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('admin/admin_messages.html', messages=msgs)

@app.route('/admin/campaigns')
def admin_campaigns():
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM budget_requests ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('admin/campaigns.html', campaigns=campaigns)

@app.route('/admin/reports')
def admin_reports():
    conn = get_db_connection()
    total_budget = conn.execute('SELECT SUM(amount) FROM budget_requests WHERE status = "Approved"').fetchone()[0] or 0
    total_pending = conn.execute('SELECT SUM(amount) FROM budget_requests WHERE status = "Pending"').fetchone()[0] or 0
    conn.close()
    return render_template('admin/reports.html', total_budget=total_budget, total_pending=total_pending)

@app.route('/admin/users')
def admin_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()
    return render_template('admin/manage_users.html', users=users)

@app.route('/admin/users/add', methods=('GET', 'POST'))
def admin_add_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO users (username, password, role) VALUES (?, ?, ?)',
                         (username, password, role))
            conn.commit()
            flash('User added successfully!')
        except sqlite3.IntegrityError:
            flash('Error: Username already exists.')
        finally:
            conn.close()
            
        return redirect(url_for('admin_users'))
        
    return render_template('admin/add_user.html')

@app.route('/admin/users/edit/<int:user_id>', methods=('GET', 'POST'))
def admin_edit_user(user_id):
    conn = get_db_connection()
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        
        if password:
            conn.execute('UPDATE users SET username = ?, password = ?, role = ? WHERE id = ?',
                         (username, password, role, user_id))
        else:
            conn.execute('UPDATE users SET username = ?, role = ? WHERE id = ?',
                         (username, role, user_id))
        conn.commit()
        conn.close()
        flash('User updated successfully!')
        return redirect(url_for('admin_users'))
    
    user = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
    conn.close()
    return render_template('admin/edit_user.html', user=user)

@app.route('/admin/site')
def admin_site():
    conn = get_db_connection()
    content = conn.execute('SELECT * FROM site_content').fetchall()
    features = conn.execute('SELECT * FROM site_features').fetchall()
    roles = conn.execute('SELECT * FROM site_roles').fetchall()
    tech = conn.execute('SELECT * FROM site_tech_stack').fetchall()
    conn.close()
    return render_template('admin/manage_site.html', content=content, features=features, roles=roles, tech=tech)

@app.route('/admin/site/content/update', methods=('POST',))
def admin_update_site_content():
    conn = get_db_connection()
    for key, value in request.form.items():
        if key.startswith('content_'):
            content_id = key.split('_')[1]
            conn.execute('UPDATE site_content SET value = ? WHERE id = ?', (value, content_id))
    conn.commit()
    conn.close()
    flash('Site content updated successfully!')
    return redirect(url_for('admin_site'))

@app.route('/admin/site/feature/update/<int:feature_id>', methods=('POST',))
def admin_update_feature(feature_id):
    title = request.form['title']
    desc = request.form['description']
    icon = request.form['icon']
    conn = get_db_connection()
    conn.execute('UPDATE site_features SET title = ?, description = ?, icon = ? WHERE id = ?', (title, desc, icon, feature_id))
    conn.commit()
    conn.close()
    flash('Feature updated!')
    return redirect(url_for('admin_site'))

@app.route('/admin/site/step/update/<int:step_id>', methods=('POST',))
def admin_update_step(step_id):
    title = request.form['title']
    desc = request.form['description']
    icon = request.form['icon']
    conn = get_db_connection()
    conn.execute('UPDATE site_steps SET title = ?, description = ?, icon = ? WHERE id = ?', (title, desc, icon, step_id))
    conn.commit()
    conn.close()
    flash('Step updated!')
    return redirect(url_for('admin_site'))

@app.route('/admin/site/tech/update/<int:tech_id>', methods=('POST',))
def admin_update_tech(tech_id):
    category = request.form['category']
    title = request.form['title']
    desc = request.form['description']
    icon = request.form['icon']
    conn = get_db_connection()
    conn.execute('UPDATE site_tech_stack SET category = ?, title = ?, description = ?, icon = ? WHERE id = ?', (category, title, desc, icon, tech_id))
    conn.commit()
    conn.close()
    flash('Tech stack item updated!')
    return redirect(url_for('admin_site'))

@app.route('/admin/users/delete/<int:user_id>', methods=('POST',))
def admin_delete_user(user_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()
    flash('User deleted successfully!')
    return redirect(url_for('admin_users'))

# --- Messaging & Global CRUD ---

@app.route('/messages/send', methods=('POST',))
def send_message():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    receiver_role = request.form['receiver_role']
    subject = request.form['subject']
    content = request.form['content']
    
    conn = get_db_connection()
    user = conn.execute('SELECT username, role FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.execute('INSERT INTO messages (sender_id, sender_name, sender_role, receiver_role, subject, content) VALUES (?, ?, ?, ?, ?, ?)',
                 (session['user_id'], user['username'], user['role'], receiver_role, subject, content))
    conn.commit()
    conn.close()
    flash('Message sent successfully!')
    
    if session['role'] == 'Admin': return redirect(url_for('admin_messages'))
    
    # Mapping for multi-word roles to their URL endpoints
    role_map = {
        'Project Supervisor': 'supervisor',
        'Marketing Team': 'marketing',
        'Content Creator': 'content',
        'Sales Team': 'sales'
    }
    
    role_path = role_map.get(session['role'], session['role'].lower())
    return redirect(url_for(f'portal_{role_path}_messages'))

@app.route('/messages/delete/<int:msg_id>', methods=('POST',))
def delete_message(msg_id):
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    # Check if user is sender or receiver (via role)
    msg = conn.execute('SELECT * FROM messages WHERE id = ?', (msg_id,)).fetchone()
    if msg:
        if msg['sender_id'] == session['user_id'] or msg['receiver_role'] == session['role'] or session['role'] == 'Admin':
            conn.execute('DELETE FROM messages WHERE id = ?', (msg_id,))
            conn.commit()
            flash('Message deleted.')
    conn.close()
    return redirect(request.referrer or url_for('index'))

# --- Content Schedule CRUD ---

@app.route('/portal/content/schedule/add', methods=('POST',))
def portal_content_add_schedule():
    title = request.form['title']
    platforms = request.form.getlist('platform')
    deadline = request.form['deadline']
    
    if not platforms:
        flash('Please select at least one platform.')
        return redirect(url_for('portal_content_schedule'))

    conn = get_db_connection()
    for platform in platforms:
        conn.execute('INSERT INTO schedule (title, platform, deadline) VALUES (?, ?, ?)',
                     (title, platform, deadline))
    conn.commit()
    conn.close()
    flash(f'Scheduled on {len(platforms)} platforms!')
    return redirect(url_for('portal_content_schedule'))

@app.route('/portal/content/schedule')
def portal_content_schedule():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    raw_items = conn.execute('SELECT * FROM schedule ORDER BY deadline ASC').fetchall()
    conn.close()
    
    # Group items by title and deadline
    grouped_items = {}
    for item in raw_items:
        key = (item['title'], item['deadline'])
        if key not in grouped_items:
            grouped_items[key] = {
                'title': item['title'],
                'deadline': item['deadline'],
                'platforms': [],
                'ids': [],
                'status': item['status'] # Taking status of first item
            }
        grouped_items[key]['platforms'].append(item['platform'])
        grouped_items[key]['ids'].append(str(item['id']))
        
    # Convert to list for template
    display_items = []
    for key, val in grouped_items.items():
        val['platform_str'] = ", ".join(val['platforms'])
        val['ids_str'] = ",".join(val['ids'])
        display_items.append(val)
        
    return render_template('portals/content_schedule.html', role='Content Creator', schedule_items=display_items)

@app.route('/portal/content/schedule/update_group', methods=('POST',))
def portal_content_update_schedule_group_status():
    ids_str = request.form['ids_str']
    new_status = request.form['status']
    id_list = ids_str.split(',')
    
    conn = get_db_connection()
    for item_id in id_list:
        conn.execute('UPDATE schedule SET status = ? WHERE id = ?', (new_status, item_id))
    conn.commit()
    conn.close()
    flash('Status updated for all selected platforms!')
    return redirect(url_for('portal_content_schedule'))

@app.route('/portal/content/schedule/delete_group', methods=('POST',))
def portal_content_delete_schedule_group():
    ids_str = request.form['ids_str']
    id_list = ids_str.split(',')
    
    conn = get_db_connection()
    for item_id in id_list:
        conn.execute('DELETE FROM schedule WHERE id = ?', (item_id,))
    conn.commit()
    conn.close()
    flash('Items removed from schedule.')
    return redirect(url_for('portal_content_schedule'))

# --- Settings Routes ---

@app.route('/admin/settings')
def admin_settings():
    return render_template('admin/settings.html')

@app.route('/admin/settings/theme', methods=('POST',))
def admin_update_theme():
    new_theme = request.form['theme']
    conn = get_db_connection()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    conn.commit()
    conn.close()
    flash('Theme updated successfully!')
    return redirect(url_for('admin_settings'))

@app.route('/admin/settings/password', methods=('POST',))
def admin_update_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = 'admin'").fetchone()
    
    if user and user['password'] == current_password:
        if new_password == confirm_password:
            conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user['id']))
            conn.commit()
            flash('Password changed successfully!')
        else:
            flash('New passwords do not match.')
    else:
        flash('Incorrect current password.')
        
    conn.close()
    return redirect(url_for('admin_settings'))

@app.route('/admin/profile')
def admin_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('admin/admin_profile.html', user=user)

@app.route('/admin/profile/update', methods=('POST',))
def admin_update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    conn = get_db_connection()
    conn.execute('UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?', (full_name, email, phone, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!')
    return redirect(url_for('admin_profile'))

# --- Portal Routes ---

@app.route('/portal/supervisor')
def portal_supervisor():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    try:
        pending_count = conn.execute('SELECT COUNT(*) FROM budget_requests WHERE status = "Pending"').fetchone()[0]
        pending_budget = conn.execute('SELECT SUM(amount) FROM budget_requests WHERE status = "Pending"').fetchone()[0] or 0
        active_campaign_count = conn.execute('SELECT COUNT(*) FROM budget_requests WHERE status = "Approved"').fetchone()[0]
        pending_requests = conn.execute('SELECT * FROM budget_requests WHERE status = "Pending" ORDER BY created_at DESC LIMIT 5').fetchall()
    except:
        pending_count = 0
        pending_budget = 0
        active_campaign_count = 0
        pending_requests = []
    conn.close()
    return render_template('portals/supervisor.html', role='Project Supervisor', 
                           pending_count=pending_count, 
                           pending_budget=pending_budget,
                           active_campaign_count=active_campaign_count,
                           pending_requests=pending_requests)

@app.route('/portal/supervisor/approvals')
def portal_supervisor_approvals():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    requests = conn.execute('SELECT * FROM budget_requests ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('portals/supervisor_approvals.html', role='Project Supervisor', requests=requests)

@app.route('/portal/supervisor/request/action/<int:request_id>', methods=('POST',))
def portal_supervisor_request_action(request_id):
    action = request.form['action']
    conn = get_db_connection()
    if action == 'approve':
        conn.execute('UPDATE budget_requests SET status = "Approved" WHERE id = ?', (request_id,))
        flash('Request approved successfully!')
    elif action == 'reject':
        conn.execute('UPDATE budget_requests SET status = "Rejected" WHERE id = ?', (request_id,))
        flash('Request rejected.')
    elif action == 'counter':
        counter_amount = request.form['counter_amount']
        conn.execute('UPDATE budget_requests SET status = "Counter-Offer", counter_amount = ? WHERE id = ?', (counter_amount, request_id))
        flash(f'Counter-offer of ${counter_amount} sent!')
    conn.commit()
    conn.close()
    return redirect(url_for('portal_supervisor_approvals'))

@app.route('/portal/supervisor/budget')
def portal_supervisor_budget():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    approved_requests = conn.execute('SELECT * FROM budget_requests WHERE status = "Approved" ORDER BY created_at DESC').fetchall()
    total_allocated = sum(r['amount'] for r in approved_requests)
    conn.close()
    return render_template('portals/supervisor_budget.html', role='Project Supervisor', transactions=approved_requests, total_allocated=total_allocated)

@app.route('/portal/supervisor/messages')
def portal_supervisor_messages():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE receiver_role = "Project Supervisor" OR sender_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('portals/supervisor_messages.html', role='Project Supervisor', messages=msgs)

@app.route('/portal/supervisor/profile')
def portal_supervisor_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('portals/supervisor_profile.html', role='Project Supervisor', user=user)

@app.route('/portal/supervisor/profile/update', methods=('POST',))
def portal_supervisor_update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    conn = get_db_connection()
    conn.execute('UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?', (full_name, email, phone, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!')
    return redirect(url_for('portal_supervisor_profile'))

@app.route('/portal/supervisor/settings')
def portal_supervisor_settings():
    return render_template('portals/supervisor_settings.html', role='Project Supervisor')

@app.route('/portal/supervisor/training', methods=('GET', 'POST'))
def portal_supervisor_training():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    if request.method == 'POST':
        trainee_name = request.form['trainee_name']
        schedule_date = request.form['schedule_date']
        workshop_purpose = request.form['workshop_purpose']
        conn.execute('INSERT INTO training_sessions (trainee_name, schedule_date, workshop_purpose) VALUES (?, ?, ?)',
                     (trainee_name, schedule_date, workshop_purpose))
        conn.commit()
        flash('Training session scheduled successfully!')
        return redirect(url_for('portal_supervisor_training'))
    
    sessions = conn.execute('SELECT * FROM training_sessions ORDER BY schedule_date DESC').fetchall()
    conn.close()
    return render_template('portals/supervisor_training.html', role='Project Supervisor', sessions=sessions)

@app.route('/portal/supervisor/settings/theme', methods=('POST',))
def portal_supervisor_update_theme():
    new_theme = request.form['theme']
    conn = get_db_connection()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    conn.commit()
    conn.close()
    flash('Theme updated successfully!')
    return redirect(url_for('portal_supervisor_settings'))

@app.route('/portal/supervisor/settings/password', methods=('POST',))
def portal_supervisor_update_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if 'user_id' not in session:
        flash('Please login to change password.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    if user and user['password'] == current_password:
        if new_password == confirm_password:
            conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user['id']))
            conn.commit()
            flash('Password changed successfully!')
        else:
            flash('New passwords do not match.')
    else:
        flash('Incorrect current password.')
        
    conn.close()
    return redirect(url_for('portal_supervisor_settings'))

@app.route('/portal/marketing')
def portal_marketing():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    campaigns = conn.execute('SELECT * FROM budget_requests WHERE proposed_by = "Marketing Team" ORDER BY created_at DESC').fetchall()
    active_count = conn.execute('SELECT COUNT(*) FROM budget_requests WHERE proposed_by = "Marketing Team" AND status = "Approved"').fetchone()[0]
    total_count = len(campaigns)
    goal_completion = int((active_count / total_count * 100)) if total_count > 0 else 0
    
    # Fetch recent inquiries for marketing
    recent_contacts = conn.execute('SELECT * FROM contacts WHERE role = "Marketing" ORDER BY submitted_at DESC LIMIT 5').fetchall()
    
    conn.close()
    return render_template('portals/marketing.html', role='Marketing Team', 
                           campaigns=campaigns, 
                           active_count=active_count, 
                           recent_contacts=recent_contacts,
                           goal_completion=goal_completion)

@app.route('/portal/marketing/request', methods=('POST',))
def portal_marketing_request():
    title = request.form['title']
    amount = request.form['amount']
    conn = get_db_connection()
    conn.execute('INSERT INTO budget_requests (title, type, amount, proposed_by) VALUES (?, ?, ?, ?)',
                 (title, 'Campaign', amount, 'Marketing Team'))
    conn.commit()
    conn.close()
    flash('Campaign budget request submitted successfully!')
    return redirect(url_for('portal_marketing'))

@app.route('/portal/marketing/campaigns')
def portal_marketing_campaigns():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    # Fetch approved and counter-offered campaigns for this specific page
    campaigns = conn.execute('SELECT b.*, u.username as assigned_username FROM budget_requests b LEFT JOIN users u ON b.assigned_to = u.id WHERE b.proposed_by = "Marketing Team" AND (b.status = "Approved" OR b.status = "Counter-Offer") ORDER BY b.created_at DESC').fetchall()
    
    # Fetch content creators for assignment dropdown
    creators = conn.execute('SELECT id, username FROM users WHERE role = "Content Creator"').fetchall()
    
    conn.close()
    return render_template('portals/marketing_campaigns.html', role='Marketing Team', campaigns=campaigns, creators=creators)

@app.route('/portal/marketing/campaign/assign/<int:campaign_id>', methods=('POST',))
def portal_marketing_assign_creator(campaign_id):
    creator_id = request.form['creator_id']
    conn = get_db_connection()
    conn.execute('UPDATE budget_requests SET assigned_to = ? WHERE id = ?', (creator_id, campaign_id))
    conn.commit()
    conn.close()
    flash('Campaign assigned to Content Creator!')
    return redirect(url_for('portal_marketing_campaigns'))

@app.route('/portal/marketing/campaign/update_progress/<int:campaign_id>', methods=('POST',))
def portal_marketing_update_progress(campaign_id):
    progress = request.form['progress']
    conn = get_db_connection()
    conn.execute('UPDATE budget_requests SET progress = ? WHERE id = ?', (progress, campaign_id))
    conn.commit()
    conn.close()
    flash('Campaign progress updated successfully!')
    return redirect(url_for('portal_marketing_campaigns'))

@app.route('/portal/marketing/messages')
def portal_marketing_messages():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE receiver_role = "Marketing Team" OR sender_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('portals/marketing_messages.html', role='Marketing Team', messages=msgs)

@app.route('/portal/marketing/profile')
def portal_marketing_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('portals/marketing_profile.html', role='Marketing Team', user=user)

@app.route('/portal/marketing/profile/update', methods=('POST',))
def portal_marketing_update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    conn = get_db_connection()
    conn.execute('UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?', (full_name, email, phone, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!')
    return redirect(url_for('portal_marketing_profile'))

@app.route('/portal/marketing/settings')
def portal_marketing_settings():
    return render_template('portals/marketing_settings.html', role='Marketing Team')

@app.route('/portal/marketing/settings/theme', methods=('POST',))
def portal_marketing_update_theme():
    new_theme = request.form['theme']
    conn = get_db_connection()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    conn.commit()
    conn.close()
    flash('Theme updated successfully!')
    return redirect(url_for('portal_marketing_settings'))

@app.route('/portal/marketing/settings/password', methods=('POST',))
def portal_marketing_update_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if 'user_id' not in session:
        flash('Please login to change password.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    if user and user['password'] == current_password:
        if new_password == confirm_password:
            conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user['id']))
            conn.commit()
            flash('Password changed successfully!')
        else:
            flash('New passwords do not match.')
    else:
        flash('Incorrect current password.')
        
    conn.close()
    return redirect(url_for('portal_marketing_settings'))

@app.route('/portal/content')
def portal_content():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    requests = conn.execute('SELECT * FROM budget_requests WHERE proposed_by = "Content Creator" ORDER BY created_at DESC').fetchall()
    
    # Fetch campaigns assigned to this creator
    assigned_campaigns = conn.execute('SELECT * FROM budget_requests WHERE assigned_to = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    
    # Fetch all strategies for this creator
    strategies = conn.execute('SELECT * FROM campaign_strategies WHERE creator_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    
    # Dashboard metrics
    scheduled_count = conn.execute('SELECT COUNT(*) FROM schedule').fetchone()[0]
    influencer_count = conn.execute('SELECT COUNT(*) FROM budget_requests WHERE type = "Influencer" AND status = "Approved"').fetchone()[0]
    
    conn.close()
    return render_template('portals/content.html', role='Content Creator', 
                           requests=requests, 
                           assigned_campaigns=assigned_campaigns, 
                           strategies=strategies,
                           scheduled_count=scheduled_count,
                           influencer_count=influencer_count)

@app.route('/portal/content/strategy/add', methods=('POST',))
def portal_content_add_strategy():
    campaign_id = request.form['campaign_id']
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('INSERT INTO campaign_strategies (campaign_id, creator_id, title, content) VALUES (?, ?, ?, ?)',
                 (campaign_id, session.get('user_id'), title, content))
    conn.commit()
    conn.close()
    flash('New strategy draft added!')
    return redirect(url_for('portal_content'))

@app.route('/portal/content/strategy/edit/<int:strategy_id>', methods=('POST',))
def portal_content_edit_strategy(strategy_id):
    title = request.form['title']
    content = request.form['content']
    
    conn = get_db_connection()
    conn.execute('UPDATE campaign_strategies SET title = ?, content = ? WHERE id = ?', (title, content, strategy_id))
    conn.commit()
    conn.close()
    flash('Strategy updated successfully!')
    return redirect(url_for('portal_content'))

@app.route('/portal/content/strategy/delete/<int:strategy_id>', methods=('POST',))
def portal_content_delete_strategy(strategy_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM campaign_strategies WHERE id = ?', (strategy_id,))
    conn.commit()
    conn.close()
    flash('Strategy deleted.')
    return redirect(url_for('portal_content'))

@app.route('/portal/content/request', methods=('POST',))
def portal_content_request():
    influencer_name = request.form['influencer_name']
    amount = request.form['amount']
    conn = get_db_connection()
    conn.execute('INSERT INTO budget_requests (title, type, amount, proposed_by) VALUES (?, ?, ?, ?)',
                 (influencer_name, 'Influencer', amount, 'Content Creator'))
    conn.commit()
    conn.close()
    flash('Influencer budget request submitted successfully!')
    return redirect(url_for('portal_content'))

@app.route('/portal/content/messages')
def portal_content_messages():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE receiver_role = "Content Creator" OR sender_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('portals/content_messages.html', role='Content Creator', messages=msgs)

@app.route('/portal/request/delete/<int:request_id>', methods=('POST',))
def portal_delete_request(request_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM budget_requests WHERE id = ?', (request_id,))
    conn.commit()
    conn.close()
    flash('Request removed.')
    return redirect(request.referrer)

@app.route('/portal/content/profile')
def portal_content_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('portals/content_profile.html', role='Content Creator', user=user)

@app.route('/portal/content/profile/update', methods=('POST',))
def portal_content_update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    conn = get_db_connection()
    conn.execute('UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?', (full_name, email, phone, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!')
    return redirect(url_for('portal_content_profile'))

@app.route('/portal/content/settings')
def portal_content_settings():
    return render_template('portals/content_settings.html', role='Content Creator')

# --- Content Upload & Review Routes ---

@app.route('/portal/content/uploads')
def portal_content_uploads():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    uploads = conn.execute('SELECT * FROM created_content WHERE creator_id = ? ORDER BY created_at DESC', (session['user_id'],)).fetchall()
    conn.close()
    return render_template('portals/content_uploads.html', role='Content Creator', uploads=uploads)

@app.route('/portal/content/upload/add', methods=('POST',))
def portal_content_upload_add():
    if 'user_id' not in session: return redirect(url_for('login'))
    title = request.form['title']
    platforms = request.form.getlist('platform')
    content_type = request.form['content_type']
    drive_link = request.form.get('drive_link')
    
    if not platforms:
        flash('Please select at least one platform.')
        return redirect(url_for('portal_content_uploads'))

    file_path = None
    if content_type == 'Graphic' and 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # Add timestamp to prevent overwriting
            from datetime import datetime
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            file_path = f"uploads/{filename}"

    conn = get_db_connection()
    for platform in platforms:
        conn.execute('INSERT INTO created_content (creator_id, title, platform, content_type, drive_link, file_path) VALUES (?, ?, ?, ?, ?, ?)',
                     (session['user_id'], title, platform, content_type, drive_link, file_path))
    conn.commit()
    conn.close()
    flash(f'Content submitted for review on {len(platforms)} platforms!')
    return redirect(url_for('portal_content_uploads'))

@app.route('/portal/marketing/review')
def portal_marketing_review():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    uploads = conn.execute('SELECT c.*, u.username as creator_name FROM created_content c JOIN users u ON c.creator_id = u.id ORDER BY c.created_at DESC').fetchall()
    conn.close()
    return render_template('portals/marketing_review.html', role='Marketing Team', uploads=uploads)

@app.route('/portal/marketing/review/action/<int:upload_id>', methods=('POST',))
def portal_marketing_content_action(upload_id):
    action = request.form['action']
    feedback = request.form.get('feedback', '')
    
    status = 'Approved' if action == 'approve' else 'Revision Requested'
    
    conn = get_db_connection()
    conn.execute('UPDATE created_content SET status = ?, feedback = ? WHERE id = ?', (status, feedback, upload_id))
    conn.commit()
    conn.close()
    flash(f'Content {status.lower()}!')
    return redirect(url_for('portal_marketing_review'))

# --- End Content Upload & Review Routes ---

@app.route('/portal/content/settings/theme', methods=('POST',))
def portal_content_update_theme():
    new_theme = request.form['theme']
    conn = get_db_connection()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    conn.commit()
    conn.close()
    flash('Theme updated successfully!')
    return redirect(url_for('portal_content_settings'))

@app.route('/portal/content/settings/password', methods=('POST',))
def portal_content_update_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if 'user_id' not in session:
        flash('Please login to change password.')
        return redirect(url_for('login'))

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    if user and user['password'] == current_password:
        if new_password == confirm_password:
            conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user['id']))
            conn.commit()
            flash('Password changed successfully!')
        else:
            flash('New passwords do not match.')
    else:
        flash('Incorrect current password.')
        
    conn.close()
    return redirect(url_for('portal_content_settings'))

@app.route('/portal/sales')
def portal_sales():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    leads_count = conn.execute('SELECT COUNT(*) FROM leads').fetchone()[0]
    total_rev = conn.execute('SELECT SUM(revenue) FROM leads WHERE status = "Closed"').fetchone()[0] or 0
    recent_leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC LIMIT 5').fetchall()
    
    # Fetch recent inquiries for sales
    recent_contacts = conn.execute('SELECT * FROM contacts WHERE role = "Sales" ORDER BY submitted_at DESC LIMIT 5').fetchall()
    
    # Sales target (hardcoded for now as placeholder for dynamic goal)
    monthly_target = 100000 
    target_completion = int((total_rev / monthly_target) * 100) if monthly_target > 0 else 0
    
    conn.close()
    return render_template('portals/sales.html', role='Sales Team', 
                           leads_count=leads_count, 
                           total_revenue=total_rev, 
                           recent_leads=recent_leads, 
                           recent_contacts=recent_contacts,
                           target_completion=target_completion)

@app.route('/portal/sales/leads')
def portal_sales_leads():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    leads = conn.execute('SELECT * FROM leads ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('portals/sales_leads.html', role='Sales Team', leads=leads)

@app.route('/portal/sales/leads/add', methods=('POST',))
def portal_sales_add_lead():
    name = request.form['name']
    email = request.form['email']
    conn = get_db_connection()
    conn.execute('INSERT INTO leads (name, email) VALUES (?, ?)', (name, email))
    conn.commit()
    conn.close()
    flash('New lead added!')
    return redirect(url_for('portal_sales_leads'))

@app.route('/portal/sales/leads/update/<int:lead_id>', methods=('POST',))
def portal_sales_update_lead(lead_id):
    status = request.form['status']
    revenue = request.form.get('revenue', 0)
    conn = get_db_connection()
    conn.execute('UPDATE leads SET status = ?, revenue = ? WHERE id = ?', (status, revenue, lead_id))
    conn.commit()
    conn.close()
    flash('Lead updated.')
    return redirect(url_for('portal_sales_leads'))

@app.route('/portal/sales/reports')
def portal_sales_reports():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    stats = conn.execute('SELECT status, COUNT(*), SUM(revenue) FROM leads GROUP BY status').fetchall()
    conn.close()
    return render_template('portals/sales_reports.html', role='Sales Team', stats=stats)

@app.route('/portal/sales/messages')
def portal_sales_messages():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    msgs = conn.execute('SELECT * FROM messages WHERE receiver_role = "Sales Team" OR sender_id = ? ORDER BY created_at DESC', (session.get('user_id'),)).fetchall()
    conn.close()
    return render_template('portals/sales_messages.html', role='Sales Team', messages=msgs)

@app.route('/portal/sales/profile')
def portal_sales_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return render_template('portals/sales_profile.html', role='Sales Team', user=user)

@app.route('/portal/sales/profile/update', methods=('POST',))
def portal_sales_update_profile():
    if 'user_id' not in session: return redirect(url_for('login'))
    full_name = request.form['full_name']
    email = request.form['email']
    phone = request.form['phone']
    conn = get_db_connection()
    conn.execute('UPDATE users SET full_name = ?, email = ?, phone = ? WHERE id = ?', (full_name, email, phone, session['user_id']))
    conn.commit()
    conn.close()
    flash('Profile updated successfully!')
    return redirect(url_for('portal_sales_profile'))

@app.route('/portal/sales/settings')
def portal_sales_settings():
    return render_template('portals/sales_settings.html', role='Sales Team')

@app.route('/portal/sales/settings/theme', methods=('POST',))
def portal_sales_update_theme():
    new_theme = request.form['theme']
    conn = get_db_connection()
    conn.execute("UPDATE settings SET value = ? WHERE key = 'theme'", (new_theme,))
    conn.commit()
    conn.close()
    flash('Theme updated successfully!')
    return redirect(url_for('portal_sales_settings'))

@app.route('/portal/sales/settings/password', methods=('POST',))
def portal_sales_update_password():
    current_password = request.form['current_password']
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    if 'user_id' not in session: return redirect(url_for('login'))
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    if user and user['password'] == current_password and new_password == confirm_password:
        conn.execute("UPDATE users SET password = ? WHERE id = ?", (new_password, user['id']))
        conn.commit()
        flash('Password changed successfully!')
    else: flash('Error updating password.')
    conn.close()
    return redirect(url_for('portal_sales_settings'))

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
