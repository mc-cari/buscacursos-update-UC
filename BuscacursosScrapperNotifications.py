from plyer import notification
import os
import platform
from BuscacursosScrapper import BuscacursosScrapper

class BuscacursosScrapperNotifications(BuscacursosScrapper):

    def __init__(self):
        super().__init__()

    def print_updated_section_info(self, section_info, prev_vacancies_available):
        
        super().print_updated_section_info(section_info, prev_vacancies_available)

        title = 'Section update'
        message = f'{section_info["Nombre"]} Update vacancies in Section {section_info["Sec."]} : {prev_vacancies_available} -> {section_info["Disponibles"]}\n'

        icon_path = os.path.join('Icons', 'Bell.ico')

        if platform.system() == 'Darwin':
            os.system("osascript -e 'display notification \"{}\" with title \"{}\"'".format(message, title))
        else:
            notification.notify(
                title = title,
                message = message,
                app_icon = icon_path,
                timeout  = 120
            )
