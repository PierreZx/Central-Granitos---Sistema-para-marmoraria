using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Producao;

public partial class ProducaoPage : ContentPage
{
	public ProducaoPage(ProducaoViewModel viewModel)
	{
		InitializeComponent();
		BindingContext = viewModel;
	}
}