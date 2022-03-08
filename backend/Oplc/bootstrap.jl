(pwd() != @__DIR__) && cd(@__DIR__) # allow starting app from bin/ dir

using Oplc
push!(Base.modules_warned_for, Base.PkgId(Oplc))
Oplc.main()
