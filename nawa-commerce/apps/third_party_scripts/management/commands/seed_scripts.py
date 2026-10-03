"""Crée des scripts tiers de démonstration (désactivés)."""
from django.core.management.base import BaseCommand
from apps.third_party_scripts.models import ThirdPartyScript


DEFAULT_SCRIPTS = [
    {
        "name": "Google Analytics 4 (démo)",
        "description": "Exemple de script GA4. Remplacez par votre ID de mesure.",
        "code": """<!-- Google Analytics 4 — REMPLACER G-XXXXXXXXXX -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'G-XXXXXXXXXX');
</script>""",
        "location": "head",
        "is_active": False,
        "require_consent": True,
    },
    {
        "name": "Meta Pixel (démo)",
        "description": "Pixel Facebook/Meta. Remplacez PIXEL_ID.",
        "code": """<!-- Meta Pixel -->
<script>
  !function(f,b,e,v,n,t,s)
  {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
  n.callMethod.apply(n,arguments):n.queue.push(arguments)};
  if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
  n.queue=[];t=b.createElement(e);t.async=!0;
  t.src=v;s=b.getElementsByTagName(e)[0];
  s.parentNode.insertBefore(t,s)}(window, document,'script',
  'https://connect.facebook.net/en_US/fbevents.js');
  fbq('init', 'PIXEL_ID');
  fbq('track', 'PageView');
</script>""",
        "location": "head",
        "is_active": False,
        "require_consent": True,
    },
]


class Command(BaseCommand):
    help = "Crée des scripts tiers de démonstration (désactivés par défaut)."

    def handle(self, *args, **options):
        created = 0
        for data in DEFAULT_SCRIPTS:
            _, was_created = ThirdPartyScript.objects.get_or_create(
                name=data["name"], defaults=data
            )
            if was_created:
                created += 1
        self.stdout.write(self.style.SUCCESS(
            f"[OK] {created} script(s) créé(s), {len(DEFAULT_SCRIPTS)} au total."
        ))
