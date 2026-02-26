using CommunityToolkit.Maui.Views;
using Marmorariacentral.Models;

namespace Marmorariacentral.Views.Orcamentos;

public partial class CadastroClientePopup : Popup
{
    private Cliente? _clienteEdicao;

    public CadastroClientePopup(Cliente? cliente = null)
    {
        InitializeComponent();
        _clienteEdicao = cliente;

        if (_clienteEdicao != null)
        {
            EntryNome.Text = _clienteEdicao.Nome;
            EntryContato.Text = _clienteEdicao.Contato;
            EntryEndereco.Text = _clienteEdicao.Endereco;
        }
    }

    private void OnCadastrarClicked(object sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(EntryNome.Text))
        {
            EntryNome.PlaceholderColor = Colors.Red;
            return;
        }

        var cliente = _clienteEdicao ?? new Cliente { Id = Guid.NewGuid().ToString(), DataCadastro = DateTime.Now };
        
        cliente.Nome = EntryNome.Text.Trim();
        cliente.Contato = EntryContato.Text?.Trim() ?? "";
        cliente.Endereco = EntryEndereco.Text?.Trim() ?? "";

        Close(cliente);
    }

    private void OnCancelarClicked(object sender, EventArgs e) => Close(null);
}