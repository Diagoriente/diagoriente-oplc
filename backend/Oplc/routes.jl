using Genie.Router

route("/") do
  serve_static_file("/welcome.html")
end

route("/one") do
    1
end

