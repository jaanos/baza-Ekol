<!DOCTYPE html>

<html>
	<head>
		<title>Skladišče podjetja Ekol</title>
		<meta http-equiv="X-UA-Compatible" content="IE=edge">
		<meta charset="utf-8" />
		<meta name="viewport" content="width=device-width, initial-scale=1, user-scalable=no" />
		<meta name="description" content="Osnovna stran skladišča Ekol" />
		<meta name="author" content="Tamara Pogačar, Matej Čušin">
		<meta name="keywords" content="Ekol" />
		
		<link rel="stylesheet" href='../static/assets/css/main.css'/>

	</head>
	<body class="is-preload">

		<!-- Header -->
			<header id="header">
				<a class="logo" href="/">Ekol</a>
				<nav>
					<a href="#menu">Meni</a>
				</nav>
			</header>

		<!-- Nav -->
			<nav id="menu">
				<ul class="links">
					<li><a href="/">Domov</a></li>
					<li><a href="uvoz_odpadka">Uvoz odpadka</a></li>
					<li><a href="izvoz_odpadka">Izvoz odpadka</a></li>
					<li><a href="pregled">Pregled skladiščenih odpadkov</a></li>
				</ul>
			</nav>

		<!-- Heading -->
			<div id="heading" >
				<h1>SKLADIŠČE</h1>
			</div>

		<!-- Main -->
			

        {{!base}}


		<!-- Footer -->
			<footer id="footer">
				<div class="inner">
					<div class="content">
						<section>
							<h4>Koristna povezava</h4>
							<ul class="plain">
								<li> <a href="https://ekorel.ekol.si/" align="right"  >Ekol d.o.o.</a> </li>
							</ul>
						</section>
					</div>
					<div class="copyright">
						% data = {"developer_name": "Tamara Pogačar in Matej Čušin", "developer_organization": "Praktična matematika, FMF"}
						% end
						&copy; 2021, {{data["developer_name"]}} ({{data["developer_organization"]}})
					</div>
				</div>
			</footer>

		<!-- Scripts -->
			<script src="../static/assets/js/jquery.min.js"></script>
			<script src="../static/assets/js/browser.min.js"></script>
			<script src="../static/assets/js/breakpoints.min.js"></script>
			<script src="../static/assets/js/util.js"></script>
			<script src="../static/assets/js/main.js"></script>
		
	</body>
</html>