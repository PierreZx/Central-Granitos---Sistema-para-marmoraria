using Marmorariacentral.ViewModels;

namespace Marmorariacentral.Views.Estoque;

public partial class EstoquePage : ContentPage
{
	public EstoquePage(EstoqueViewModel viewModel)
	{
		InitializeComponent();
		BindingContext = viewModel;

		if (viewModel != null) 
        System.Diagnostics.Debug.WriteLine("=== ESTOQUE: ViewModel OK ===");
	}
}
