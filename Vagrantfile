require "ipaddr"

def parse_integer_env(name, default)
  value = Integer(ENV.fetch(name, default), 10)
  raise "#{name} must be greater than 0" if value < 1

  value
rescue ArgumentError
  raise "#{name} must be a valid integer"
end

def parse_ipv4_env(name, default)
  value = ENV.fetch(name, default)
  ip = IPAddr.new(value)
  raise "#{name} must be a valid IPv4 address" unless ip.ipv4?

  value
rescue IPAddr::InvalidAddressError
  raise "#{name} must be a valid IPv4 address"
end

def truthy_env?(name, default)
  %w[1 true yes on].include?(ENV.fetch(name, default).downcase)
end

VM_CPUS = parse_integer_env("RADIOACTIVE_FOOT_PI_CPUS", "2")
VM_MEMORY = parse_integer_env("RADIOACTIVE_FOOT_PI_MEMORY", "2048")
VM_HOSTNAME = ENV.fetch("RADIOACTIVE_FOOT_PI_HOSTNAME", "radioactive-foot-pi")
VM_OS = ENV.fetch("RADIOACTIVE_FOOT_PI_OS", "ubuntu").downcase
LAN_ENABLED = truthy_env?("RADIOACTIVE_FOOT_PI_LAN", "true")
LAN_IP = parse_ipv4_env("RADIOACTIVE_FOOT_PI_LAN_IP", "192.168.56.10")
WAN_ACKNOWLEDGED = truthy_env?("RADIOACTIVE_FOOT_PI_WAN_ACKNOWLEDGE", "false")
WAN_BRIDGE = ENV["RADIOACTIVE_FOOT_PI_WAN_BRIDGE"]&.strip
WAN_BRIDGE = nil if WAN_BRIDGE == ""
WAN_ENABLED = truthy_env?("RADIOACTIVE_FOOT_PI_WAN", "false")

BOXES = {
  "ubuntu" => "bento/ubuntu-22.04",
  "fedora" => "bento/fedora-40"
}.freeze

box = BOXES.fetch(VM_OS) do
  raise "Unsupported RADIOACTIVE_FOOT_PI_OS '#{VM_OS}'. Supported values (case-insensitive): #{BOXES.keys.join(', ')}"
end

Vagrant.configure("2") do |config|
  config.vm.box = box
  config.vm.hostname = VM_HOSTNAME

  if LAN_ENABLED
    config.vm.network "private_network", ip: LAN_IP
  end

  if WAN_ENABLED
    unless WAN_ACKNOWLEDGED
      raise "RADIOACTIVE_FOOT_PI_WAN requires RADIOACTIVE_FOOT_PI_WAN_ACKNOWLEDGE=true because bridged networking exposes the guest to the host network"
    end

    if WAN_BRIDGE.nil?
      raise "RADIOACTIVE_FOOT_PI_WAN requires RADIOACTIVE_FOOT_PI_WAN_BRIDGE to avoid interactive network selection"
    end

    config.vm.network "public_network", bridge: WAN_BRIDGE
  end

  config.vm.provider "virtualbox" do |provider|
    provider.memory = VM_MEMORY
    provider.cpus = VM_CPUS
  end
end
