export function formatE164Like(input) {
    let v = String(input || "");
  
    // mantém + e números
    v = v.replace(/[^\d+]/g, "");
  
    // garante só um +
    if (v.includes("+")) {
      v = "+" + v.replace(/\+/g, "");
    }
  
    // se começar sem +, sugere +55
    if (!v.startsWith("+")) v = "+55" + v;
  
    // limita tamanho (E.164 máx 15 dígitos + sinal)
    const plus = v.startsWith("+") ? "+" : "";
    const digits = v.replace(/\D/g, "").slice(0, 15);
    return plus + digits;
  }
  