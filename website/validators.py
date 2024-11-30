from django.core.exceptions import ValidationError
import re

class PasswordStrengthValidator:
    def validate(self, password, user=None):
        if not re.findall('[A-Z]', password):
            raise ValidationError(
                'Password must contain at least 1 uppercase letter.',
                code='password_no_upper',
            )
        if not re.findall('[a-z]', password):
            raise ValidationError(
                'Password must contain at least 1 lowercase letter.',
                code='password_no_lower',
            )
        if not re.findall('[0-9]', password):
            raise ValidationError(
                'Password must contain at least 1 number.',
                code='password_no_number',
            )
        if not re.findall('[^A-Za-z0-9]', password):
            raise ValidationError(
                'Password must contain at least 1 special character.',
                code='password_no_special',
            )

    def get_help_text(self):
        return """
        Your password must contain at least:
        * 1 uppercase letter
        * 1 lowercase letter
        * 1 number
        * 1 special character
        """ 