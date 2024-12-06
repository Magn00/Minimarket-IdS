from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from core.tasks import enviar_notificaciones  # Importa la tarea

# Define la función al nivel superior
def delete_old_job_executions(max_age=604_800):
    """Elimina registros antiguos de ejecuciones de tareas (más de 7 días por defecto)."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "default")

    # Agrega la tarea para enviar notificaciones
    scheduler.add_job(
        enviar_notificaciones,  
         trigger=CronTrigger(minute="*/1"),  
        id="enviar_notificaciones",
        max_instances=1,
        replace_existing=True,
    )
    print("Tarea 'enviar_notificaciones' registrada.")

    # Limpieza de ejecuciones antiguas
    scheduler.add_job(
        delete_old_job_executions,  # Ahora se puede serializar correctamente
        trigger=CronTrigger(day_of_week="mon", hour="00", minute="00"),
        id="delete_old_job_executions",
        max_instances=1,
        replace_existing=True,
    )
    print("Tarea 'delete_old_job_executions' registrada.")

    scheduler.start()
    print("Scheduler iniciado.")


