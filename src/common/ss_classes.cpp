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

void ClientBase::GetParts(std::vector<Parts::PartInstance>& partList)
{
	if (m_OutputBuffer.empty())
		return;

	if (m_OutputLock.try_lock())
	{
		for (auto& part : m_OutputBuffer)
		{
			partList.push_back(std::move(part));
		}
		m_OutputBuffer.clear();
	m_OutputLock.unlock();
	}
}