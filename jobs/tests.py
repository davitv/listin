from django.test import TestCase
from django.contrib.auth import get_user_model
from .forms import CVForm

User = get_user_model()

CV_CORRECT_DATA = {
    'name': "Some Fancy New CV",
    'about': "About me goes looong here...",

    'education-0-university': "MIT",
    'education-0-department': "Electronics and quantum mechanics",
    'education-0-specialization': "Engineer",
    'education-0-degree': "2",

    'education-1-university': "Berkley",
    'education-1-department': "Motorsports Faculty",
    'education-1-specialization': "Rear motorbike weel specialist",
    'education-1-degree': "3",

    'skill-0-name': "Python",
    'skill-0-level': "3",

    'skill-1-name': "PostgreSQL",
    'skill-1-level': "2",

    'skill-2-name': "Java",
    'skill-2-level': "1",

    'skill-3-name': "C++",
    'skill-3-level': "4",

    'experience-0-organization': "United donuts Inc.",
    'experience-0-position': "Tolerant to people",
    'experience-0-region': "GB",
    'experience-0-date_from': "2001-02-23",
    'experience-0-date_to': "2004-03-23",

    'experience-1-organization': "Second United donuts Incs.",
    'experience-1-position': "Not THAT Tolerant to people",
    'experience-1-region': "RU",
    'experience-1-website': "http://big-boobies.us.com/",
    'experience-1-date_from': "2004-04-12",
    'experience-1-date_to': "2007-10-17",

    'experience-2-organization': "Final Boobies Corp.",
    'experience-2-position': "Definately not tolerante at all manager",
    'experience-2-region': "AU",
    'experience-2-website': "http://big-boobies-updated.us.com/",
    'experience-2-date_from': "2007-11-20",
    'experience-2-date_to': "2016-04-20",

    'language-0-name': "English",
    'language-0-level': "3",

    'language-1-name': "Russian",
    'language-1-level': "4",

    'language-2-name': "Franch",
    'language-2-level': "2",
}


class TestCVForm(TestCase):
    def setUp(self):
        self.user = User.objects._create_user('test@test.com', '123')

    def test_correct_data_create(self):
        form = CVForm(data=CV_CORRECT_DATA, initial={
            'user': self.user
        })
        self.assertTrue(form.is_valid(), form.errors.as_text())
        instance = form.save()

        self.assertEqual(instance.education_set.count(), 2)
        self.assertEqual(instance.skill_set.count(), 4)
        self.assertEqual(instance.experience_set.count(), 3)
        self.assertEqual(instance.language_set.count(), 3)

    def test_correct_data_update(self):
        form = CVForm(data=CV_CORRECT_DATA, initial={
            'user': self.user
        })
        self.assertTrue(form.is_valid(), form.errors.as_text())
        instance = form.save()

        self.assertEqual(instance.education_set.count(), 2)
        self.assertEqual(instance.skill_set.count(), 4)
        self.assertEqual(instance.experience_set.count(), 3)
        self.assertEqual(instance.language_set.count(), 3)
        cv = self.user.cv_set.first()
        updated_data = dict(
            name='New name',
            about="New About",
        )
        updated_data.update(CV_CORRECT_DATA)
        for i, education in enumerate(instance.education_set.all()):
            updated_data["education-%s-university" % (i, )] = 'modified_' + education.university
            updated_data["education-%s-department" % (i, )] = 'modified_' + education.department
            updated_data["education-%s-pk" % (i, )] = education.pk

        for i, skill in enumerate(instance.skill_set.all()):
            updated_data["skill-%s-name" % (i, )] = 'modified_' + skill.name
            updated_data["skill-%s-pk" % (i, )] = skill.pk

        for i, language in enumerate(instance.language_set.all()):
            updated_data["language-%s-name" % (i, )] = 'modified_' + language.name
            updated_data["language-%s-pk" % (i, )] = language.pk

        for i, experience in enumerate(instance.experience_set.all()):
            updated_data["experience-%s-organization" % (i, )] = 'modified_' + experience.organization
            updated_data["experience-%s-pk" % (i, )] = experience.pk

        update_form = CVForm(instance=cv, data=updated_data, initial={
            'user': self.user
        })
        self.assertTrue(update_form.is_valid(), update_form.errors.as_text())
        updated_instance = update_form.save()

        self.assertEqual(instance.education_set.count(), 2)
        self.assertEqual(instance.skill_set.count(), 4)
        self.assertEqual(instance.experience_set.count(), 3)
        self.assertEqual(instance.language_set.count(), 3)

        self.assertEqual(
            instance.education_set.filter(university=updated_data['education-0-university']).count(),
            1, updated_data['education-0-university']
        )

        self.assertEqual(
            instance.skill_set.filter(name=updated_data['skill-0-name']).count(),
            1, updated_data['skill-0-name']
        )

        self.assertEqual(
            instance.language_set.filter(name=updated_data['language-0-name']).count(),
            1, updated_data['language-0-name']
        )

        self.assertEqual(
            instance.experience_set.filter(organization=updated_data['experience-0-organization']).count(),
            1, updated_data['experience-0-organization']
        )

    def test_correct_related_remove(self):
        form = CVForm(data=CV_CORRECT_DATA, initial={
            'user': self.user
        })
        self.assertTrue(form.is_valid(), form.errors.as_text())
        instance = form.save()
        cv = self.user.cv_set.first()
        updated_data = {
            "name": 'New name',
            "about": "New About",
            "education-0-DELETE": '1',
            "education-0-pk": str(instance.education_set.all()[0].pk),
            "education-1-DELETE": '1',
            "education-1-pk": str(instance.education_set.all()[1].pk),
            "skill-0-pk": str(instance.skill_set.all()[0].pk),
            "skill-0-DELETE": '1',
            "skill-1-pk": str(instance.skill_set.all()[1].pk),
            "skill-1-DELETE": str(instance.skill_set.all()[1].pk)
        }
        self.assertTrue('education-0-DELETE' in updated_data)
        update_form = CVForm(instance=cv, data=updated_data, initial={
            'user': self.user
        })
        self.assertTrue(update_form.is_valid(), update_form.errors.as_text())

        updated_instance = update_form.save()
        self.assertEqual(update_form.instance, form.instance)
        self.assertEqual(updated_instance.education_set.count(), 0)
        self.assertEqual(updated_instance.skill_set.count(), 2)


class TestCVSerializer(TestCase):
    pass

