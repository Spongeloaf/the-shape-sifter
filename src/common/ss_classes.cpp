#include "ss_classes.h"

namespace BeltBuckleInterface
{
	string BbPacket::GetString()
	{
		CalcCSUM();
		return kStartPacket + m_command.m_string + m_payload + m_CSUM + kEndPacket;
	}

	void BbPacket::CalcCSUM()
	{
		// TODO: Actually implement checksums.
		m_CSUM = "CSUM";
	}
}	//namespace BeltBuckleInterface

