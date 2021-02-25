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

// The server calls this method to retrieve output parts from the client
void ClientBase::SendPartsToServer(PartList& partList)
{
	if (m_OutputLock.try_lock())
	{
		if (!m_OutputBuffer.empty())
		{
			for (auto& part : m_OutputBuffer)
			{
				// This should automagically overwrite any part in the list with new contents, or add new parts.
				partList[part.first] = std::move(part.second);
			}
			m_OutputBuffer.clear();
		}
	m_OutputLock.unlock();
	}
}

// The server call this method to send parts to this client
void ClientBase::SendPartsToCLient(Parts::PartInstance& part)
{
	if (m_InputLock.try_lock())
	{
		m_InputBuffer[part.m_ID] = part;
		m_InputLock.unlock();
	}
}