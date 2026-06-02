from database import db
from models.task import Task
from models.user import User
from models.category import Category
from sqlalchemy.orm import joinedload
from datetime import datetime


def _serialize_task(task):
    data = task.to_dict()
    data['overdue'] = task.is_overdue()
    return data


def _serialize_task_with_relations(task):
    data = _serialize_task(task)
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def list_tasks():
    tasks = Task.query.options(
        joinedload(Task.user), joinedload(Task.category)
    ).all()
    return [_serialize_task_with_relations(t) for t in tasks], 200


def get_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    return _serialize_task(task), 200


def create_task(data):
    if not data:
        return {'error': 'Dados inválidos'}, 400

    title = data.get('title')
    if not title:
        return {'error': 'Título é obrigatório'}, 400
    if len(title) < 3:
        return {'error': 'Título muito curto'}, 400
    if len(title) > 200:
        return {'error': 'Título muito longo'}, 400

    status = data.get('status', 'pending')
    if status not in Task.VALID_STATUSES:
        return {'error': 'Status inválido'}, 400

    priority = data.get('priority', 3)
    if priority < 1 or priority > 5:
        return {'error': 'Prioridade deve ser entre 1 e 5'}, 400

    user_id = data.get('user_id')
    if user_id and not User.query.get(user_id):
        return {'error': 'Usuário não encontrado'}, 404

    category_id = data.get('category_id')
    if category_id and not Category.query.get(category_id):
        return {'error': 'Categoria não encontrada'}, 404

    task = Task()
    task.title = title
    task.description = data.get('description', '')
    task.status = status
    task.priority = priority
    task.user_id = user_id
    task.category_id = category_id

    due_date = data.get('due_date')
    if due_date:
        try:
            task.due_date = datetime.strptime(due_date, '%Y-%m-%d')
        except (ValueError, TypeError):
            return {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 400

    tags = data.get('tags')
    if tags:
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    db.session.add(task)
    db.session.commit()
    return task.to_dict(), 201


def update_task(task_id, data):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    if not data:
        return {'error': 'Dados inválidos'}, 400

    if 'title' in data:
        if len(data['title']) < 3:
            return {'error': 'Título muito curto'}, 400
        if len(data['title']) > 200:
            return {'error': 'Título muito longo'}, 400
        task.title = data['title']

    if 'description' in data:
        task.description = data['description']

    if 'status' in data:
        if data['status'] not in Task.VALID_STATUSES:
            return {'error': 'Status inválido'}, 400
        task.status = data['status']

    if 'priority' in data:
        if data['priority'] < 1 or data['priority'] > 5:
            return {'error': 'Prioridade deve ser entre 1 e 5'}, 400
        task.priority = data['priority']

    if 'user_id' in data:
        if data['user_id'] and not User.query.get(data['user_id']):
            return {'error': 'Usuário não encontrado'}, 404
        task.user_id = data['user_id']

    if 'category_id' in data:
        if data['category_id'] and not Category.query.get(data['category_id']):
            return {'error': 'Categoria não encontrada'}, 404
        task.category_id = data['category_id']

    if 'due_date' in data:
        if data['due_date']:
            try:
                task.due_date = datetime.strptime(data['due_date'], '%Y-%m-%d')
            except (ValueError, TypeError):
                return {'error': 'Formato de data inválido'}, 400
        else:
            task.due_date = None

    if 'tags' in data:
        tags = data['tags']
        task.tags = ','.join(tags) if isinstance(tags, list) else tags

    task.updated_at = datetime.utcnow()
    db.session.commit()
    return task.to_dict(), 200


def delete_task(task_id):
    task = Task.query.get(task_id)
    if not task:
        return {'error': 'Task não encontrada'}, 404
    db.session.delete(task)
    db.session.commit()
    return {'message': 'Task deletada com sucesso'}, 200


def search_tasks(query, status, priority, user_id):
    tasks_q = Task.query
    if query:
        tasks_q = tasks_q.filter(
            db.or_(Task.title.like(f'%{query}%'), Task.description.like(f'%{query}%'))
        )
    if status:
        tasks_q = tasks_q.filter(Task.status == status)
    if priority:
        tasks_q = tasks_q.filter(Task.priority == int(priority))
    if user_id:
        tasks_q = tasks_q.filter(Task.user_id == int(user_id))
    return [t.to_dict() for t in tasks_q.all()], 200


def task_stats():
    total = Task.query.count()
    pending = Task.query.filter_by(status='pending').count()
    in_progress = Task.query.filter_by(status='in_progress').count()
    done = Task.query.filter_by(status='done').count()
    cancelled = Task.query.filter_by(status='cancelled').count()

    overdue_count = Task.query.filter(
        Task.due_date < datetime.utcnow(),
        Task.status.notin_(['done', 'cancelled'])
    ).count()

    return {
        'total': total,
        'pending': pending,
        'in_progress': in_progress,
        'done': done,
        'cancelled': cancelled,
        'overdue': overdue_count,
        'completion_rate': round((done / total) * 100, 2) if total > 0 else 0
    }, 200
