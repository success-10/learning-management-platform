import django_filters
from apps.courses.models import Course


class CourseFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(lookup_expr='icontains')
    instructor = django_filters.CharFilter(
        field_name='instructor__username', lookup_expr='icontains'
    )
    is_published = django_filters.BooleanFilter()

    class Meta:
        model = Course
        fields = ['is_published', 'title', 'instructor']
