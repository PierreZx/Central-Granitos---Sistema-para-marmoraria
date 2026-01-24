import 'package:flutter/material.dart';
import '../../core/utils/constants.dart';

class LoginPage extends StatefulWidget {
  // 🔑 Necessário para o app.dart liberar as rotas após o login
  final Function(String) onLoginSuccess;

  const LoginPage({super.key, required this.onLoginSuccess});

  @override
  State<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  final TextEditingController emailController = TextEditingController(text: AUTH_EMAIL);
  final TextEditingController senhaController = TextEditingController();

  bool loading = false;

  void showSnack(String msg, {bool success = true}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          msg,
          style: const TextStyle(color: COLOR_WHITE, fontWeight: FontWeight.w500),
        ),
        backgroundColor: success ? Colors.green.shade600 : Colors.red.shade600,
        behavior: SnackBarBehavior.floating,
        margin: const EdgeInsets.all(20),
      ),
    );
  }

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
    if (email == 'acesso.producao@gmail.com' && senha == 'MarmorariaC55') {
      widget.onLoginSuccess('producao'); // Atualiza estado global
      showSnack('Bem-vindo à Área de Produção!');
      Navigator.pushReplacementNamed(context, '/producao');
      return;
    }

    // 2️⃣ ADMIN / GERAL
    if (email == AUTH_EMAIL && senha == AUTH_PASSWORD) {
      widget.onLoginSuccess('admin'); // Atualiza estado global
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
        // ✅ SingleChildScrollView resolve o erro de Overflow no celular
        child: SingleChildScrollView(
          child: Container(
            width: 400,
            margin: const EdgeInsets.all(20),
            padding: const EdgeInsets.all(40),
            decoration: BoxDecoration(
              color: COLOR_WHITE,
              borderRadius: BorderRadius.circular(24),
              boxShadow: [
                BoxShadow(
                  blurRadius: 30,
                  color: Colors.black.withValues(alpha: 0.05),
                  offset: const Offset(0, 10),
                )
              ],
            ),
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                Container(
                  padding: const EdgeInsets.all(15),
                  decoration: BoxDecoration(
                    color: COLOR_PRIMARY.withValues(alpha: 0.1),
                    borderRadius: BorderRadius.circular(15),
                  ),
                  child: const Icon(
                    Icons.precision_manufacturing_rounded,
                    size: 40,
                    color: COLOR_PRIMARY,
                  ),
                ),
                const SizedBox(height: 20),
                const Text(
                  'CENTRAL GRANITOS',
                  style: TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    letterSpacing: 1,
                    color: COLOR_PRIMARY,
                  ),
                ),
                const Text(
                  'Sistema de Gestão Interna',
                  style: TextStyle(fontSize: 14, color: Colors.grey),
                ),
                const SizedBox(height: 30),
                TextField(
                  controller: emailController,
                  decoration: InputDecoration(
                    labelText: 'E-mail',
                    prefixIcon: const Icon(Icons.email_outlined),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onSubmitted: (_) => realizarLogin(),
                ),
                const SizedBox(height: 15),
                TextField(
                  controller: senhaController,
                  obscureText: true,
                  decoration: InputDecoration(
                    labelText: 'Senha',
                    prefixIcon: const Icon(Icons.lock_outline),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  onSubmitted: (_) => realizarLogin(),
                ),
                const SizedBox(height: 20),
                SizedBox(
                  width: double.infinity,
                  height: 55,
                  child: ElevatedButton(
                    onPressed: loading ? null : realizarLogin,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: COLOR_PRIMARY,
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                    ),
                    child: loading
                        ? const CircularProgressIndicator(color: COLOR_WHITE)
                        : const Text('Entrar', style: TextStyle(color: COLOR_WHITE, fontWeight: FontWeight.bold)),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}