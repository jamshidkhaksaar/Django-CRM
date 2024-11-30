"""
Run script for the Django project.
"""

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "Django-CRM.asgi:application",
        host="127.0.0.1",
        port=8000,
        reload=True
    ) 