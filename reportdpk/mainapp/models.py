from django.db import models


class Direction(models.Model):
    """ Направления (СОУТ, Энергоаудит и т.д.)
    Методы: crm.dealcategory.list => [{ID: ..., NAME: ...}, ...];
            crm.deal.fields => UF_CRM_1610523951 => [{ID: ..., VALUE: ...}, ...] - для направления 43 (отдел продаж)
    """
    id_bx = models.PositiveIntegerField(primary_key=True, verbose_name='ID направления в BX24',
                                        unique=True, db_index=True)
    name = models.CharField(verbose_name='Название направления', max_length=50)
    new = models.BooleanField(verbose_name='Новое напрвление', default=True, db_index=True)
    general_id_bx = models.IntegerField(verbose_name='ID направления в BX24 (для совместимости со старыми направлениями)')

    def __str__(self):
        return f"{self.id_bx} - {self.general_id_bx}. {self.name}"

    class Meta:
        verbose_name = 'Направление сделки'
        verbose_name_plural = 'Направления сделок'


STATUS_DEAL_CHOICES = [
    ("PREPARATION", 'Подготовка к работе'),
    ("WORK", 'В работе'),
    ("SUCCESSFUL", 'Успешна'),
    ("FAILURE", 'Провалена'),
]


class Stage(models.Model):
    """ Стадия сделки """
    id_bx = models.PositiveIntegerField(primary_key=True, verbose_name='ID стадии в BX24', unique=True, db_index=True)
    abbrev = models.CharField(verbose_name='Аббревиатура стадии сделки', unique=True, max_length=35, db_index=True)
    name = models.CharField(verbose_name='Название стадии сделки', max_length=150)
    won = models.BooleanField(verbose_name='Сделка завершена успешно', default=False, db_index=True)
    status = models.CharField(max_length=11, choices=STATUS_DEAL_CHOICES, blank=True, null=True, db_index=True)
    direction = models.ForeignKey(Direction, verbose_name='Направление', on_delete=models.CASCADE, related_name='stage',
                                  blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.abbrev} - {self.name}"

    class Meta:
        verbose_name = 'Стадия сделки'
        verbose_name_plural = 'Стадии сделки'


class Company(models.Model):
    """ Компания """
    id_bx = models.PositiveIntegerField(primary_key=True, verbose_name='ID компании в BX24', unique=True, db_index=True)
    name = models.CharField(verbose_name="Название компании", max_length=300, blank=True, null=True, db_index=True)
    inn = models.CharField(verbose_name='ИНН компании', max_length=15, blank=True, null=True, db_index=True)
    date_last_communication = models.DateTimeField(verbose_name='Дата последней коммуникации', blank=True, null=True)
    responsible = models.PositiveIntegerField(verbose_name='ID ответственого в BX24',
                                              blank=True, null=True, db_index=True)
    industry = models.CharField(verbose_name='Сфера деятельности', max_length=25, blank=True, null=True, db_index=True)
    sector = models.CharField(verbose_name='Отрасль', max_length=100, blank=True, null=True, db_index=True)
    region = models.CharField(verbose_name='Регион', max_length=100, blank=True, null=True, db_index=True)
    source = models.CharField(verbose_name='Источник компании', max_length=100, blank=True, null=True, db_index=True)
    number_employees = models.IntegerField(verbose_name='Количество сотрудников', blank=True, null=True, db_index=True)
    address = models.CharField(verbose_name='Адрес компании', max_length=300, blank=True, null=True)
    district = models.CharField(verbose_name='Район области', max_length=100, blank=True, null=True)
    main_activity = models.CharField(verbose_name='Основной вид деятельности', max_length=500, blank=True, null=True)
    other_activities = models.CharField(verbose_name='Другие виды деятельности', max_length=2000, blank=True, null=True)
    revenue = models.DecimalField(verbose_name='Годовой оборот', max_digits=15, decimal_places=2, default=0,
                                  blank=True, null=True, db_index=True)
    profit = models.DecimalField(verbose_name='Чистая прибыль', max_digits=15, decimal_places=2, default=0,
                                 blank=True, null=True)
    requisite_region = models.CharField(verbose_name='Реквизит - район', max_length=100,
                                        blank=True, null=True, db_index=True)
    requisites_city = models.CharField(verbose_name='Реквизит - город', max_length=50,
                                       blank=True, null=True, db_index=True)
    requisites_province = models.CharField(verbose_name='Реквизит - область', max_length=50,
                                           blank=True, null=True, db_index=True)

    def __str__(self):
        return f"{self.id_bx}. {self.name or ' - '}"

    class Meta:
        verbose_name = 'Компания'
        verbose_name_plural = 'Компании'


class Deal(models.Model):
    """ Сделка """
    id_bx = models.PositiveIntegerField(primary_key=True, verbose_name='id сделки в BX24', unique=True, db_index=True)
    title = models.CharField(verbose_name='Название сделки', max_length=350, blank=True, null=True, db_index=True)
    date_create = models.DateTimeField(verbose_name='Дата создания сделки', blank=True, null=True)
    date_modify = models.DateTimeField(verbose_name='Дата последнего изменения', blank=True, null=True)
    date_closed = models.DateTimeField(verbose_name='Дата завершения сделки', blank=True, null=True)
    date_last_communication = models.DateTimeField(verbose_name='Дата последней коммуникации', blank=True, null=True)
    closed = models.BooleanField(verbose_name='Сделка завершена', default=False)
    opportunity = models.DecimalField(verbose_name='Сумма сделки', max_digits=15, decimal_places=2, default=0,
                                      blank=True, null=True)
    balance_on_payments = models.DecimalField(verbose_name='Остаток по оплатам', max_digits=15, decimal_places=2,
                                              default=0, blank=True, null=True)
    amount_paid = models.DecimalField(verbose_name='Всего оплат на сумму', max_digits=15, decimal_places=2,
                                      default=0, blank=True, null=True)
    company = models.ForeignKey(Company, verbose_name='Компания', on_delete=models.CASCADE, related_name='deal',
                                blank=True, null=True)
    direction = models.ForeignKey(Direction, verbose_name='Направление', on_delete=models.CASCADE, related_name='deal',
                                  blank=True, null=True, db_index=True)
    stage = models.ForeignKey(Stage, verbose_name='Стадия', on_delete=models.CASCADE, related_name='deal',
                              blank=True, null=True)

    def __str__(self):
        return f"{self.id_bx}. {self.title or ' - '}"

    class Meta:
        verbose_name = 'Сделка'
        verbose_name_plural = 'Сделки'


STATUS_CALL_TYPE = [
    ("1", 'Исходящий'),
    ("2", 'Входящий'),
    ("3", 'Входящий с перенаправлением'),
    ("4", 'Обратный звонок'),
]


class Calls(models.Model):
    id_bx = models.PositiveIntegerField(primary_key=True, verbose_name='ID звонка в BX24', unique=True, db_index=True)
    call_type = models.CharField(max_length=1, choices=STATUS_CALL_TYPE, blank=True, null=True, db_index=True)
    duration = models.PositiveIntegerField(verbose_name='Продолжительность звонка')
    start_date = models.DateTimeField(verbose_name='Время инициализации звонка')
    activity_id = models.PositiveIntegerField(verbose_name='Идентификатор дела CRM')
    company = models.ForeignKey(Company, verbose_name='Компания', on_delete=models.CASCADE, related_name='calls',
                                blank=True, null=True)

    def __str__(self):
        return f"{self.id_bx}. {self.start_date}"

    class Meta:
        verbose_name = 'Звонок'
        verbose_name_plural = 'Звонки'

