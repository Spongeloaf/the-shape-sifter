from shape_sifter_tools.shape_sifter_tools import PartInstance, SuipLadle, BbPacket


packet = BbPacket(serial_string='<A0000123456789QWECSUM>')

part1 = PartInstance(instance_id='12345')
part2 = PartInstance(instance_id='12345')
part3 = PartInstance(instance_id='12345')

part_list = [part1,part2,part3]

ladle = SuipLadle('Test', 'Part instance', part_list)

for attr, value in part1.__dict__.items():
    print(value)

