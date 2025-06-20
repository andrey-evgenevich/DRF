from rest_framework.pagination import PageNumberPagination


class CoursePaginator(PageNumberPagination):
    page_size = 5  # Количество курсов на странице по умолчанию
    page_size_query_param = "page_size"  # Параметр для изменения количества элементов
    max_page_size = 50  # Максимальное количество элементов на странице


class LessonPaginator(PageNumberPagination):
    page_size = 10  # Количество уроков на странице по умолчанию
    page_size_query_param = "page_size"
    max_page_size = 100
