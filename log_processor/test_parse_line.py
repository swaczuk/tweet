#!/usr/bin/env python3
"""
Test simple para verificar el parsing de una línea real
"""

line = '''127.0.0.1 - - 25/09/2025 01:27:38 AM "GET http://localhost/ HTTP/1.1" 200 100 100  "" "IIS Application Initialization Preload"'''

print("Línea original:")
print(line)
print("\n" + "="*80)

# Método actual
last_quote_start = line.rfind('"', 0, -1)
last_quote_end = line.rfind('"')
user_agent_v1 = line[last_quote_start + 1:last_quote_end] if last_quote_start != -1 and last_quote_end != -1 else ""

print("\nMétodo actual (rfind):")
print(f"  last_quote_start: {last_quote_start}")
print(f"  last_quote_end: {last_quote_end}")
print(f"  user_agent: '{user_agent_v1}'")

# Método alternativo: encontrar todas las comillas y tomar las últimas dos
parts = line.split('"')
print("\n" + "="*80)
print(f"\nMétodo alternativo (split):")
print(f"  Número de partes: {len(parts)}")
for i, part in enumerate(parts):
    if part:
        print(f"  Parte {i}: '{part[:80]}'")

if len(parts) >= 6:
    user_agent_v2 = parts[-2]
    print(f"\n  User agent (parte -2): '{user_agent_v2}'")

# Método 3: Buscar después del status code
print("\n" + "="*80)
print("\nMétodo 3 (buscar después de status):")

# Encontrar el request
first_quote = line.find('"')
second_quote = line.find('"', first_quote + 1)
request = line[first_quote + 1:second_quote]
print(f"  Request: '{request}'")

# Después del request
after_request = line[second_quote + 1:]
print(f"  Después de request: '{after_request[:100]}'")

# El user agent está en el último par de comillas no vacío
remaining_parts = after_request.split('"')
print(f"  Partes restantes: {len(remaining_parts)}")
for i, part in enumerate(remaining_parts):
    if part.strip() and part.strip() not in ['', '""']:
        print(f"    Parte {i}: '{part[:80]}'")

# El último elemento no vacío es el user agent
for i in range(len(remaining_parts) - 1, -1, -1):
    if remaining_parts[i].strip() and remaining_parts[i].strip() not in ['', '""']:
        user_agent_v3 = remaining_parts[i].strip()
        print(f"\n  User agent encontrado en parte {i}: '{user_agent_v3}'")
        break
