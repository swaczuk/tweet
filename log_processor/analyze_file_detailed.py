#!/usr/bin/env python3
"""
Análisis detallado línea por línea del archivo real
"""
import sys
from log_parser import LogParser


def analyze_first_n_lines(file_path, n=100):
    """Analiza las primeras N líneas en detalle"""
    print("="*80)
    print(f"ANÁLISIS DETALLADO DE LAS PRIMERAS {n} LÍNEAS")
    print("="*80)

    parser = LogParser()

    parsed_count = 0
    failed_count = 0
    bot_count = 0
    empty_ua_count = 0

    failed_samples = []

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        for line_num, line in enumerate(f, 1):
            if line_num > n:
                break

            line = line.strip()
            if not line:
                continue

            # Intentar parsear
            entry = parser.parse_line(line)

            if entry:
                parsed_count += 1
                bot_count += 1
            else:
                # No se parseó - ver por qué
                match = parser.LOG_PATTERN.match(line)
                if match:
                    # El regex hizo match pero no se detectó bot
                    data = match.groupdict()
                    ua = data.get('user_agent') or data.get('user_agent_noq') or ''

                    if not ua or ua.strip() == '':
                        empty_ua_count += 1
                    else:
                        # Tiene UA pero no es bot
                        parsed_count += 1
                        if len(failed_samples) < 10:
                            failed_samples.append({
                                'line_num': line_num,
                                'line': line,
                                'ua': ua,
                                'url': data['url']
                            })
                else:
                    # El regex NO hizo match
                    failed_count += 1

    print(f"\nResultados de las primeras {n} líneas:")
    print("-"*80)
    print(f"  Bots detectados:       {bot_count}")
    print(f"  User agents vacíos:    {empty_ua_count}")
    print(f"  UA no-bot:             {len(failed_samples)}")
    print(f"  Regex no match:        {failed_count}")
    print(f"  Total procesado:       {bot_count + empty_ua_count + len(failed_samples) + failed_count}")

    if failed_samples:
        print(f"\n📝 EJEMPLOS DE USER AGENTS QUE NO SON BOTS:")
        print("-"*80)
        for sample in failed_samples[:5]:
            print(f"\nLínea {sample['line_num']}:")
            print(f"  URL: {sample['url'][:60]}...")
            print(f"  UA: {sample['ua'][:100]}...")


def sample_random_lines(file_path, sample_size=50):
    """Toma una muestra aleatoria de líneas"""
    print("\n" + "="*80)
    print(f"MUESTRA ALEATORIA DE {sample_size} LÍNEAS")
    print("="*80)

    import random

    # Leer todas las líneas
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        all_lines = [line.strip() for line in f if line.strip()]

    # Tomar muestra aleatoria
    sample = random.sample(all_lines, min(sample_size, len(all_lines)))

    parser = LogParser()

    bot_count = 0
    empty_ua = 0
    no_bot = 0
    no_match = 0

    for line in sample:
        entry = parser.parse_line(line)
        if entry:
            bot_count += 1
        else:
            match = parser.LOG_PATTERN.match(line)
            if match:
                data = match.groupdict()
                ua = data.get('user_agent') or data.get('user_agent_noq') or ''
                if not ua or ua.strip() == '':
                    empty_ua += 1
                else:
                    no_bot += 1
            else:
                no_match += 1

    print(f"\nResultados de la muestra:")
    print("-"*80)
    print(f"  Bots detectados:       {bot_count} ({bot_count/sample_size*100:.1f}%)")
    print(f"  User agents vacíos:    {empty_ua} ({empty_ua/sample_size*100:.1f}%)")
    print(f"  UA no-bot:             {no_bot} ({no_bot/sample_size*100:.1f}%)")
    print(f"  Regex no match:        {no_match} ({no_match/sample_size*100:.1f}%)")

    # Proyección al archivo completo
    bot_rate = bot_count / sample_size
    print(f"\n📊 PROYECCIÓN AL ARCHIVO COMPLETO:")
    print("-"*80)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        total_lines = sum(1 for line in f if line.strip())

    expected_bots = int(total_lines * bot_rate)
    print(f"  Total de líneas: {total_lines:,}")
    print(f"  Bots esperados: {expected_bots:,} ({bot_rate*100:.1f}%)")


def check_line_endings(file_path):
    """Verifica qué tipo de line endings tiene el archivo"""
    print("\n" + "="*80)
    print("ANÁLISIS DE LINE ENDINGS")
    print("="*80)

    with open(file_path, 'rb') as f:
        content = f.read(10000)  # Primeros 10KB

    lf_count = content.count(b'\n')
    crlf_count = content.count(b'\r\n')
    cr_count = content.count(b'\r') - crlf_count

    print(f"\nEn los primeros 10KB:")
    print(f"  LF (\\n):       {lf_count}")
    print(f"  CRLF (\\r\\n):  {crlf_count}")
    print(f"  CR (\\r):       {cr_count}")

    if crlf_count > 0:
        print(f"\n  ⚠️  Archivo usa Windows line endings (CRLF)")
    elif lf_count > 0:
        print(f"\n  ✅ Archivo usa Unix line endings (LF)")
    elif cr_count > 0:
        print(f"\n  ⚠️  Archivo usa Mac line endings (CR)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python analyze_file_detailed.py <archivo_log.txt>")
        sys.exit(1)

    file_path = sys.argv[1]

    # Análisis 1: Primeras 100 líneas
    analyze_first_n_lines(file_path, n=100)

    # Análisis 2: Muestra aleatoria
    sample_random_lines(file_path, sample_size=200)

    # Análisis 3: Line endings
    check_line_endings(file_path)

    print("\n" + "="*80)
    print("CONCLUSIÓN")
    print("="*80)
    print("\nSi la proyección muestra ~26.5% de bots, entonces el problema NO es")
    print("el código del parser, sino que:")
    print("  1. La mayoría del tráfico NO es de bots (es tráfico humano normal)")
    print("  2. Los user agents vacíos son legítimos")
    print("  3. El parser está funcionando correctamente")
    print("\nSi la proyección muestra >80% de bots, entonces hay un problema")
    print("con cómo se lee el archivo y necesitamos investigar más.")
    print()
