using Microsoft.AspNetCore.Mvc.RazorPages;

namespace BlazorApp.Models
{
    public class IndexModel : PageModel
    {
        public const string SessionKeyName = "_Name";
        public const string SessionKeyAge = "_Age";

       // private readonly ILogger<IndexModel> _logger;

        public IndexModel()
        {
            //_logger = logger;
        }

         
    }
}
