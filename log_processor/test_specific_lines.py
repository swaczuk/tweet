#!/usr/bin/env python3
"""
Test específico para las líneas problemáticas del archivo real
"""
from log_parser import LogParser
import re


def test_specific_lines():
    """Prueba líneas específicas que sabemos que tienen bots"""

    # Estas son líneas reales del archivo que DEBERÍAN detectar bots pero no lo hacen
    test_lines = [
        # Línea 1 - Tiene Googlebot
        '10.240.191.25 - - 09/09/2025 03:02:19 AM "GET https://www.ajg.com/ca-fr/team/shannon-millar/ HTTP/1.1" 200 100 100  "" "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.154 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"',

        # Líneas con UA vacío (esperado que no se detecten)
        '10.240.191.25 - - 09/09/2025 03:02:22 AM "GET https://www.ajg.com/uk/ HTTP/1.1" 200 100 100  "" ""',

        # Línea con campos faltantes
        '10.240.191.29 - - 09/09/2025 03:02:25 AM "GET https://www.gallagherbassett.com/au/workers-compensation/new-south-wales/contact-page/ HTTP/1.1" 200 100',

        # Línea que SÍ funcionó
        '10.240.191.26 - - 09/09/2025 03:02:19 AM "GET https://www.ajg.com/tr-en/ HTTP/1.1" 200 100 100  "" "Pingdom.com_bot_version_1.4_(http://www.pingdom.com/)"',
    ]

    parser = LogParser()

    print("="*80)
    print("TEST DE LÍNEAS ESPECÍFICAS")
    print("="*80)

    for i, line in enumerate(test_lines, 1):
        print(f"\n{'='*80}")
        print(f"LÍNEA {i}:")
        print(f"{'='*80}")
        print(f"Input: {line[:120]}...")

        # Probar el regex directamente
        match = parser.LOG_PATTERN.match(line)
        if match:
            data = match.groupdict()
            print(f"\n✅ REGEX MATCH:")
            print(f"  IP: {data['ip']}")
            print(f"  Status: {data['status']}")
            print(f"  URL: {data['url'][:60]}...")
            print(f"  user_agent (quoted): '{data.get('user_agent', 'None')}'")
            print(f"  user_agent_noq (unquoted): '{data.get('user_agent_noq', 'None')}'")

            # Ver cuál user agent se selecciona
            user_agent = data.get('user_agent') or data.get('user_agent_noq') or ''
            print(f"\n  User Agent seleccionado: '{user_agent[:100] if user_agent else '(vacío)'}...'")

            if user_agent:
                bot = parser.identify_bot(user_agent)
                if bot:
                    print(f"  🤖 Bot detectado: {bot}")
                else:
                    print(f"  ❌ No se detectó bot en este user agent")
            else:
                print(f"  ⚠️  User agent vacío - línea será descartada")
        else:
            print(f"\n❌ REGEX NO MATCH")
            print("  El regex no captura esta línea")

        # Probar parse_line completo
        print(f"\n  Resultado de parse_line():")
        entry = parser.parse_line(line)
        if entry:
            print(f"  ✅ Parseada exitosamente como: {entry.bot_name} en {entry.region}")
        else:
            print(f"  ❌ parse_line() retornó None")

    print(f"\n{'='*80}")


def test_regex_variations():
    """Prueba diferentes variaciones del regex"""
    print("\n\n" + "="*80)
    print("PROBANDO VARIACIONES DEL REGEX")
    print("="*80)

    # La línea problemática con Googlebot
    test_line = '10.240.191.25 - - 09/09/2025 03:02:19 AM "GET https://www.ajg.com/ca-fr/team/shannon-millar/ HTTP/1.1" 200 100 100  "" "Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5X Build/MMB29P) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.7258.154 Mobile Safari/537.36 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"'

    # Regex super simple para user agent
    simple_ua = re.compile(r'"([^"]*)"[^"]*$')

    print("\nLínea de prueba (con Googlebot):")
    print(f"{test_line[:120]}...")

    match = simple_ua.search(test_line)
    if match:
        ua = match.group(1)
        print(f"\n✅ User Agent extraído con regex simple:")
        print(f"  {ua}")
        print(f"\n  ¿Contiene 'Googlebot'? {('Googlebot' in ua)}")

    # Ahora probar con el regex completo del parser
    parser = LogParser()
    match2 = parser.LOG_PATTERN.match(test_line)
    if match2:
        data = match2.groupdict()
        ua_quoted = data.get('user_agent', '')
        ua_unquoted = data.get('user_agent_noq', '')
        ua_final = ua_quoted or ua_unquoted

        print(f"\n❌ User Agent extraído con LOG_PATTERN del parser:")
        print(f"  user_agent (quoted): '{ua_quoted[:100] if ua_quoted else '(vacío)'}...'")
        print(f"  user_agent_noq: '{ua_unquoted[:100] if ua_unquoted else '(vacío)'}...'")
        print(f"  Final seleccionado: '{ua_final[:100] if ua_final else '(vacío)'}...'")
        print(f"\n  ¿Contiene 'Googlebot'? {('Googlebot' in ua_final) if ua_final else False}")

    print("\n" + "="*80)


if __name__ == "__main__":
    test_specific_lines()
    test_regex_variations()
