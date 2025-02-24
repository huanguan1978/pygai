<nav class="navbar navbar-expand-lg navbar-light bg-light">
  <a class="navbar-brand" href="/admin/">PyGai</a>
  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNavAltMarkup" aria-controls="navbarNavAltMarkup" aria-expanded="false" aria-label="Toggle navigation">
    <span class="navbar-toggler-icon"></span>
  </button>
  <div class="collapse navbar-collapse" id="navbarNavAltMarkup">
    <ul class="navbar-nav mr-auto">
      <li class="nav-item">  
        <a class="nav-link" href="/admin/topic/">Topic</a>
      </li>
      <li class="nav-item">  
        <a class="nav-link" href="/admin/instruct/">Instruct</a>
      </li>
      <li class="nav-item">    
        <a class="nav-link" href="/admin/config/">Config</a>
      </li>
      <li class="nav-item">    
        <a class="nav-link" href="/admin/directory/">Directory</a>
      </li>
      <li class="nav-item">   
        <a class="nav-link" href="/admin/prompt/">Prompt</a>
      </li>
      <li class="nav-item">  
        <a class="nav-link" href="/admin/content/">Content</a>
      </li>
    </ul>
  </div>
</nav>


% if defined('alert'):
<!-- alert begin -->
<div>
% for key, vals in alert.items():
  <div class="alert alert-{{key}}" role="alert">
    {{ '<br/>'.join(vals) }}
  </div>
% end
</div>
<!-- alert end -->
% end

<script type="text/javascript" defer="defer">

var pathname = window.location.pathname;
$('document').ready(function(event){

  // admin menu selected begin
  var admin_menu = pathname.match(/admin\/(.*?)\//i) ;
  if(admin_menu){
    admin_menu = admin_menu[1];
    $('.nav-link').each(function(idx, dat){
	    var href = $(dat).attr('href');
	    if(href.indexOf(admin_menu) !== -1){
	      $(dat).addClass('active');
	    }
    });
  }
  // admin menu selected end


}); // jq.ready end

</script>