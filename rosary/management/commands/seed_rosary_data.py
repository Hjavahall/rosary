from django.core.management.base import BaseCommand
from django.utils.timezone import now
from rosary.models import Prayer, MysterySet, Mystery, DecadeStep, PrayerSequence, PrayerSequenceStep


PRAYERS = {
    "Sign of the Cross": (
        "In the name of the Father, and of the Son, and of the Holy Spirit. Amen."
    ),
    "Apostles' Creed": (
        "I believe in God, the Father almighty, Creator of Heaven and earth. "
        "And in Jesus Christ, His only Son, our Lord, Who was conceived by the Holy Spirit, "
        "born of the Virgin Mary, suffered under Pontius Pilate; was crucified, died, and was buried. "
        "He descended into Hell. The third day He rose again from the dead. He ascended into Heaven, "
        "and sits at the right hand of God, the Father almighty. He shall come again to judge the living and the dead. "
        "I believe in the Holy Spirit, the holy Catholic Church, the communion of saints, the forgiveness of sins, "
        "the resurrection of the body, and life everlasting. Amen."
    ),
    "Our Father": (
        "Our Father, Who art in Heaven, hallowed be Thy Name. Thy kingdom come, Thy will be done on earth as it is in Heaven. "
        "Give us this day our daily bread, and forgive us our trespasses, as we forgive those who trespass against us. "
        "And lead us not into temptation, but deliver us from evil. Amen."
    ),
    "Hail Mary": (
        "Hail Mary, full of grace, the Lord is with thee. Blessed art thou among women, "
        "and blessed is the fruit of thy womb, Jesus. Holy Mary, Mother of God, pray for us sinners, "
        "now and at the hour of our death. Amen."
    ),
    "Glory Be": (
        "Glory be to the Father, and to the Son, and to the Holy Spirit. "
        "As it was in the beginning is now, and ever shall be, world without end. Amen."
    ),
    "Fatima Prayer": (
        "O my Jesus, forgive us our sins, save us from the fires of Hell; lead all souls to Heaven, "
        "especially those in most need of Thy mercy. Amen."
    ),
    "Hail Holy Queen": (
        "Hail Holy Queen, mother of mercy; our life, our sweetness, and our hope. "
        "To thee do we cry, poor banished children of Eve. To thee do we send up our sighs, "
        "mourning and weeping in this vale of tears. Turn, then, most gracious advocate, thine eyes of mercy toward us. "
        "And after this, our exile, show unto us the blessed fruit of thy womb, Jesus. "
        "O clement, O loving, O sweet Virgin Mary. Pray for us, O holy Mother of God, "
        "that we may be made worthy of the promises of Christ. Amen."
    ),
    "Closing Prayer": (
        "O God, whose only-begotten Son by His life, death and resurrection, has purchased for us the rewards of eternal life; "
        "grant, we beseech Thee, that by meditating upon these mysteries of the Most Holy Rosary of the Blessed Virgin Mary, "
        "we may imitate what they contain and obtain what they promise, through the same Christ our Lord. Amen."
    ),
}

MYSTERY_SETS = {
    "Joyful": {
        "days": "Monday, Saturday",
        "mysteries": [
            ("The Annunciation", "Luke 1:26-38"),
            ("The Visitation", "Luke 1:39-56"),
            ("The Nativity", "Luke 2:1-21"),
            ("The Presentation", "Luke 2:22-38"),
            ("The Finding in the Temple", "Luke 2:41-52"),
        ]
    },
    "Sorrowful": {
        "days": "Tuesday, Friday",
        "mysteries": [
            ("The Agony in the Garden", "Matthew 26:36-56"),
            ("The Scourging at the Pillar", "Matthew 27:26"),
            ("The Crowning with Thorns", "Matthew 27:27-31"),
            ("The Carrying of the Cross", "Matthew 27:32"),
            ("The Crucifixion", "Matthew 27:33-56"),
        ]
    },
    "Glorious": {
        "days": "Wednesday, Sunday",
        "mysteries": [
            ("The Resurrection", "John 20:1-29"),
            ("The Ascension", "Luke 24:36-53"),
            ("The Descent of the Holy Spirit", "Acts 2:1-41"),
            ("The Assumption", ""),
            ("The Coronation of Mary", "")
        ]
    },
    "Luminous": {
        "days": "Thursday",
        "mysteries": [
            ("The Baptism of Jesus", "Matthew 3:13-16"),
            ("The Wedding at Cana", "John 2:1-11"),
            ("The Proclamation of the Kingdom", "Mark 1:14-15"),
            ("The Transfiguration", "Matthew 17:1-8"),
            ("The Institution of the Eucharist", "Matthew 26"),
        ]
    }
}

class Command(BaseCommand):
    help = "Seeds the Rosary prayers and mysteries using full text."

    def handle(self, *args, **kwargs):
        # Create all base prayers
        prayer_objs = {}
        for name, text in PRAYERS.items():
            prayer, _ = Prayer.objects.get_or_create(name=name, defaults={"text": text})
            prayer_objs[name] = prayer

        self.stdout.write(self.style.SUCCESS("✅ Core prayers created."))

        # Create Mystery Sets and their Mysteries
        for set_name, set_data in MYSTERY_SETS.items():
            mystery_set, _ = MysterySet.objects.get_or_create(name=set_name, defaults={"days": set_data["days"]})

            for idx, (title, reference) in enumerate(set_data["mysteries"], start=1):
                mystery, _ = Mystery.objects.get_or_create(
                    set=mystery_set,
                    title=title,
                    defaults={"scripture_reference": reference}
                )

                # Add decade structure
                DecadeStep.objects.update_or_create(
                    mystery=mystery, order=1,
                    defaults={"prayer": prayer_objs["Our Father"], "repeat": 1}
                )
                DecadeStep.objects.update_or_create(
                    mystery=mystery, order=2,
                    defaults={"prayer": prayer_objs["Hail Mary"], "repeat": 10}
                )
                DecadeStep.objects.update_or_create(
                    mystery=mystery, order=3,
                    defaults={"prayer": prayer_objs["Glory Be"], "repeat": 1}
                )
                DecadeStep.objects.update_or_create(
                    mystery=mystery, order=4,
                    defaults={"prayer": prayer_objs["Fatima Prayer"], "repeat": 1}
                )
                        # Introductory sequence
        intro_sequence, _ = PrayerSequence.objects.get_or_create(name="Introductory Prayers")
        intro_steps = [
            ("Sign of the Cross", 1),
            ("Apostles' Creed", 1),
            ("Our Father", 1),
            ("Hail Mary", 3),
            ("Glory Be", 1),
            ("Fatima Prayer", 1)
        ]
        for order, (prayer_name, repeat) in enumerate(intro_steps, start=1):
            PrayerSequenceStep.objects.update_or_create(
                sequence=intro_sequence, order=order,
                defaults={"prayer": prayer_objs[prayer_name], "repeat": repeat}
            )

        # Concluding sequence
        conclusion_sequence, _ = PrayerSequence.objects.get_or_create(name="Concluding Prayers")
        conclusion_steps = [
            ("Hail Holy Queen", 1),
            ("Closing Prayer", 1),
            ("Sign of the Cross", 1)
        ]
        for order, (prayer_name, repeat) in enumerate(conclusion_steps, start=1):
            PrayerSequenceStep.objects.update_or_create(
                sequence=conclusion_sequence, order=order,
                defaults={"prayer": prayer_objs[prayer_name], "repeat": repeat}
            )

        self.stdout.write(self.style.SUCCESS("✅ Intro and conclusion sequences created."))

