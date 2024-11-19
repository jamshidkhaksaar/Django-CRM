from django.db.models import Q
from functools import lru_cache
from enum import Enum
from typing import Dict, Any

@lru_cache(maxsize=None)
def get_status_mapping():
    return {
        'data_entry': {
            'can_edit': True,
            'can_delete': False,
            'can_approve': False
        },
        'deputy_director': {
            'can_edit': False,
            'can_delete': False,
            'can_approve': True,
            'approval_stage': 'pending_deputy'
        },
        'executive_director': {
            'can_edit': False,
            'can_delete': False,
            'can_approve': True,
            'approval_stage': 'pending_executive'
        },
        'chief_executive': {
            'can_edit': False,
            'can_delete': False,
            'can_approve': True,
            'approval_stage': 'pending_chief'
        },
        'superadmin': {
            'can_edit': True,
            'can_delete': True,
            'can_approve': True
        }
    }

def get_user_pending_records(user):
    status_map = get_status_mapping().get(user.user_type)
    if not status_map:
        return Q()
    
    return Q(**{
        f"{status_map['status_field']}": status_map['pending_value']
    }) 

def get_dashboard_cards(user, records):
    """Helper function to generate dashboard cards based on user type"""
    try:
        cards = [
            {
                'title': 'Total Records',
                'value': records.count(),
                'bg_class': 'bg-primary'
            },
            {
                'title': 'Approved Records',
                'value': records.filter(cashier_status='Approved').count(),
                'bg_class': 'bg-success'
            },
            {
                'title': 'Pending Records',
                'value': records.filter(cashier_status='Pending').count(),
                'bg_class': 'bg-warning'
            },
            {
                'title': 'Rejected Records',
                'value': records.filter(cashier_status='Rejected').count(),
                'bg_class': 'bg-danger'
            }
        ]
        
        # Add role-specific cards
        if user.user_type == 'cashier':
            cards.append({
                'title': 'My Transactions',
                'value': records.filter(requester=user).count(),
                'bg_class': 'bg-info'
            })
            
        return cards
        
    except Exception as e:
        logger.error(f"Error generating dashboard cards: {str(e)}", exc_info=True)
        return [] 

class RecordStatus(Enum):
    PENDING = 'Pending'
    APPROVED = 'Approved'
    REJECTED = 'Rejected'
    FIRST_APPROVAL = 'first_approval'
    SECOND_APPROVAL = 'second_approval'

def get_user_status_context(user, records) -> Dict[str, Any]:
    """Unified status context generator for both views"""
    context = {
        'user_type': user.get_user_type_display(),
        'total_records': records.count()
    }
    
    status_mapping = get_status_mapping().get(user.user_type, {})
    if status_mapping:
        status_field = status_mapping['status_field']
        pending_value = status_mapping['pending_value']
        
        context.update({
            'pending_records': records.filter(**{status_field: pending_value}).count(),
            'my_records': records.filter(requester=user).count() if user.user_type == 'cashier' else None
        })
    
    return context 