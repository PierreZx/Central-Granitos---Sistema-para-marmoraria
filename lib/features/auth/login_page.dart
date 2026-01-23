import 'package:flutter/material.dart';

import '../../core/utils/constants.dart';

class LoginPage extends StatefulWidget {
  const LoginPage({super.key});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController emailController =
      TextEditingController(text: AUTH_EMAIL); // facilitador dev
  final TextEditingController senhaController = TextEditingController();

  bool loading = false;

  // 🔔 SnackBar (equivalente ao show_snack)
  void showSnack(String msg, {bool success = true}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          msg,
          style: const TextStyle(
            color: COLOR_WHITE,
            fontWeight: FontWeight.w500,
          ),
        ),
        backgroundColor:
            success ? Colors.green.shade600 : Colors.red.shade600,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(20),
      ),
    );
  }

  // 🔐 Login (equivalente ao realizar_login)
  Future<void> realizarLogin() async {
    setState(() => loading = true);

    final email = emailController.text.trim();
    final senha = senhaController.text.trim();

    if (email.isEmpty || senha.isEmpty) {
      showSnack('Por favor, preencha todos os campos!', success: false);
      setState(() => loading = false);
      return;
    }

    // 1️⃣ ACESSO PRODUÇÃO
    if (email == 'acesso.producao@gmail.com' &&
        senha == 'MarmorariaC55') {
      // depois isso vira Provider / Session
      showSnack('Bem-vindo à Área de Produção!');
      Navigator.pushReplacementNamed(context, '/producao');
      return;
    }

    // 2️⃣ ADMIN / GERAL
    if (email == AUTH_EMAIL && senha == AUTH_PASSWORD) {
      showSnack('Acesso autorizado. Bem-vindo!');
      Navigator.pushReplacementNamed(context, '/dashboard');
    } else {
      showSnack('E-mail ou senha inválidos.', success: false);
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: COLOR_BACKGROUND,
      body: Center(
        child: Container(
          width: 400,
          padding: const EdgeInsets.all(40),
          decoration: BoxDecoration(
            color: COLOR_WHITE,
            borderRadius: BorderRadius.circular(24),
            boxShadow: [
              BoxShadow(
                blurRadius: 30,
                color: Colors.black.withOpacity(0.1),
                offset: const Offset(0, 10),
              )
            ],
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              // 🔧 Ícone
              Container(
                padding: const EdgeInsets.all(15),
                decoration: BoxDecoration(
                  color: COLOR_PRIMARY.withOpacity(0.15),
                  borderRadius: BorderRadius.circular(15),
                ),
                child: const Icon(
                  Icons.precision_manufacturing_rounded,
                  size: 40,
                  color: COLOR_PRIMARY,
                ),
              ),

              const SizedBox(height: 20),

              // 🏷️ Título
              Column(
                children: const [
                  Text(
                    'CENTRAL GRANITOS',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      letterSpacing: 1,
                      color: COLOR_PRIMARY,
                    ),
                  ),
                  SizedBox(height: 2),
                  Text(
                    'Sistema de Gestão Interna',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.grey,
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 30),

              // 📧 Email
              TextField(
                controller: emailController,
                decoration: InputDecoration(
                  labelText: 'E-mail',
                  hintText: 'seu@email.com',
                  prefixIcon: const Icon(Icons.email_outlined),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: COLOR_PRIMARY),
                  ),
                ),
                onSubmitted: (_) => realizarLogin(),
              ),

              const SizedBox(height: 15),

              // 🔑 Senha
              TextField(
                controller: senhaController,
                obscureText: true,
                decoration: InputDecoration(
                  labelText: 'Senha',
                  prefixIcon: const Icon(Icons.lock_outline),
                  filled: true,
                  fillColor: Colors.grey.shade50,
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  focusedBorder: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12),
                    borderSide: const BorderSide(color: COLOR_PRIMARY),
                  ),
                ),
                onSubmitted: (_) => realizarLogin(),
              ),

              const SizedBox(height: 8),

              // 🔗 Esqueceu senha
              Align(
                alignment: Alignment.centerRight,
                child: Text(
                  'Esqueceu a senha? Contate o administrador.',
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey.shade500,
                  ),
                ),
              ),

              const SizedBox(height: 20),

              // ▶️ Botão Entrar
              SizedBox(
                width: double.infinity,
                height: 55,
                child: ElevatedButton(
                  onPressed: loading ? null : realizarLogin,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: COLOR_PRIMARY,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 2,
                  ),
                  child: loading
                      ? const SizedBox(
                          width: 22,
                          height: 22,
                          child: CircularProgressIndicator(
                            strokeWidth: 2,
                            color: COLOR_WHITE,
                          ),
                        )
                      : const Text(
                          'Entrar',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: COLOR_WHITE,
                          ),
                        ),
                ),
              ),

              const SizedBox(height: 15),

              // 🧾 Versão
              Text(
                'v2.0.1',
                style: TextStyle(
                  fontSize: 10,
                  color: Colors.grey.shade400,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
