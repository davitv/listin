# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-08-27 11:42
from __future__ import unicode_literals

import core.models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import django_countries.fields
import phonenumber_field.modelfields
import versatileimagefield.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=30, verbose_name='last name')),
                ('userpic', versatileimagefield.fields.VersatileImageField(blank=True, null=True, upload_to='customer/userpics', verbose_name='profile userpic')),
                ('userpic_ppoi', versatileimagefield.fields.PPOIField(default='0.5x0.5', editable=False, max_length=20, verbose_name='Image PPOI')),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, max_length=128, null=True, verbose_name='phone number')),
                ('email', models.EmailField(max_length=254, unique=True, verbose_name='email address')),
                ('birth_date', models.DateField(blank=True, null=True, verbose_name='birth date')),
                ('country', django_countries.fields.CountryField(blank=True, max_length=2, null=True)),
                ('state', models.CharField(blank=True, max_length=300, null=True, verbose_name='State/region')),
                ('city', models.CharField(blank=True, max_length=300, null=True, verbose_name='city/village')),
                ('is_email_confirmed', models.BooleanField(default=False, verbose_name='mail confirmed')),
                ('is_phone_confirmed', models.BooleanField(default=False, verbose_name='phone confirmed')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', core.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Branch',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Company name', max_length=300)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('state', models.CharField(blank=True, max_length=300, null=True)),
                ('city', models.CharField(blank=True, max_length=300, null=True)),
                ('address_1', models.CharField(max_length=300)),
                ('address_2', models.CharField(blank=True, max_length=300, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Branch',
                'verbose_name_plural': 'Branches',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200, verbose_name='Category name')),
                ('description', models.TextField(blank=True, null=True, verbose_name='About this category')),
                ('icon', versatileimagefield.fields.VersatileImageField(blank=True, help_text='Category icon', null=True, upload_to='categories/icons')),
            ],
            options={
                'verbose_name': 'Category',
                'verbose_name_plural': 'Categories',
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name='HTMLWidgetModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.TextField(default='', null=True)),
                ('slug', models.TextField(db_index=True, max_length=200)),
            ],
            options={
                'verbose_name': 'HTML Widget',
                'verbose_name_plural': 'HTML Widgets',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, verbose_name='Organization url slug')),
                ('logo', versatileimagefield.fields.VersatileImageField(blank=True, help_text='Company logo', null=True, upload_to='company/logo')),
                ('image', versatileimagefield.fields.VersatileImageField(blank=True, help_text='Company page image', null=True, upload_to='company/page')),
                ('name', models.CharField(help_text='Company name', max_length=300)),
                ('inn', models.CharField(max_length=300)),
                ('ogrn', models.CharField(max_length=300)),
                ('url', models.URLField(blank=True, null=True)),
                ('country', django_countries.fields.CountryField(max_length=2)),
                ('state', models.CharField(blank=True, max_length=300, null=True)),
                ('city', models.CharField(blank=True, max_length=300, null=True)),
                ('address_1', models.CharField(max_length=300)),
                ('address_2', models.CharField(blank=True, max_length=300, null=True)),
                ('email', models.EmailField(max_length=254)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
                ('description', models.TextField(blank=True, null=True)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
                ('is_confirmed', models.PositiveIntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Organization',
                'verbose_name_plural': 'Organizations',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='OrganizationProduct',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_featured', models.BooleanField(default=False, verbose_name='company featured')),
                ('is_popular', models.BooleanField(default=False, verbose_name='bestseller')),
                ('rate_up', models.PositiveIntegerField(blank=True, default=0, verbose_name='Green bulb')),
                ('rate_down', models.PositiveIntegerField(blank=True, default=0, verbose_name='Red bulb')),
                ('rate_broken', models.PositiveIntegerField(blank=True, default=0, verbose_name='Broken bulb')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Partnership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(blank=True, choices=[(0, 'Partnership is not confirmed by partner'), (1, 'Partnership is confirmed by partner'), (2, 'Partnership is declined by partner')], default=0)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Partnership',
                'verbose_name_plural': 'Partnerships',
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_positive', models.BooleanField()),
            ],
            options={
                'verbose_name': 'Rating',
                'verbose_name_plural': 'Ratings',
            },
        ),
        migrations.CreateModel(
            name='Staff',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('position', models.CharField(blank=True, max_length=40, null=True, verbose_name='position')),
                ('is_verified', models.PositiveIntegerField(blank=True, default=0)),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Staff',
                'verbose_name_plural': 'Staff',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Vacancy',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=300, verbose_name='Vacancy position name')),
                ('description', models.TextField(verbose_name='Extended description')),
                ('date_added', models.DateTimeField(auto_now_add=True)),
                ('date_modified', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Vacancy',
                'verbose_name_plural': 'Vacancies',
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='VisitorMessage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(blank=True, max_length=200, null=True)),
                ('email', models.EmailField(help_text='Email to reply', max_length=254)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(blank=True, help_text='Phone for callback', max_length=128, null=True)),
                ('text', models.TextField()),
                ('ip', models.CharField(blank=True, help_text='IP from which message was sent', max_length=200, null=True)),
                ('send_to', models.PositiveIntegerField(blank=True, choices=[(0, 'Send to organization page'), (1, 'Send to organization email')], default=0, verbose_name='Kind of submited message')),
                ('is_deleted', models.BooleanField(default=False)),
                ('is_confirmed', models.BooleanField(default=False)),
                ('phone_status', models.PositiveIntegerField(blank=True, choices=[(0, 'Phone is not verified'), (1, 'Phone is verified'), (2, 'Verification was sent')], default=0)),
                ('email_status', models.PositiveIntegerField(blank=True, choices=[(0, 'Email is not verified'), (1, 'Email is verified')], default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Organization')),
                ('user', models.ForeignKey(blank=True, help_text='Authed user id', null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
